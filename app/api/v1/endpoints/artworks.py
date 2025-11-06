# app/api/v1/endpoints/artworks.py
import logging
from typing import List, Optional
from PIL import Image
import base64
import io

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import verify_api_key
from app.database import get_db
from app.models.artist import Artist
from app.models.artwork import Artwork
from app.models.exhibition import Exhibition
from app.models.reaction import Reaction
from app.schemas.artwork import (
    ArtworkCreate,
    ArtworkDetail,
    ArtworkMatchRequest,
    ArtworkMatchResponse,
    ArtworkResponse,
    ArtworkUpdate,
)
from app.utils.lambda_client import lambda_client
from fastapi import APIRouter, Depends, HTTPException, Query, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/artworks", tags=["Artworks"])


@router.get(
    "",
    response_model=List[ArtworkResponse],
    summary="작품 목록 조회",
    description="작품 목록을 조회합니다. artist_id와 exhibition_id로 필터링 가능합니다.",
)
def get_artworks(
    artist_id: Optional[int] = Query(None, description="작가 ID"),
    exhibition_id: Optional[int] = Query(None, description="전시 ID"),
    db: Session = Depends(get_db),
):
    """
    작품 목록 조회 (가벼운 버전)

    Args:
        artist_id: 작가 ID로 필터링
        exhibition_id: 전시 ID로 필터링

    Returns:
        List[ArtworkResponse]: 작품 목록 (artist_name, reaction_count 포함)

    Raises:
        404: 존재하지 않는 artist_id 또는 exhibition_id
    """
    # Artist 존재 여부 확인
    if artist_id:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작가 ID {artist_id}를 찾을 수 없습니다",
            )

    # Exhibition 존재 여부 확인
    if exhibition_id:
        exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
        if not exhibition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"전시 ID {exhibition_id}를 찾을 수 없습니다",
            )

    # 쿼리 구성 (artist와 reaction_count join)
    query = (
        db.query(
            Artwork,
            Artist.name.label("artist_name"),
            func.count(Reaction.id).label("reaction_count")
        )
        .join(Artist, Artwork.artist_id == Artist.id)
        .outerjoin(Reaction, Artwork.id == Reaction.artwork_id)
        .group_by(Artwork.id, Artist.name)
    )

    if artist_id:
        query = query.filter(Artwork.artist_id == artist_id)

    if exhibition_id:
        query = query.join(Artwork.exhibitions).filter(Exhibition.id == exhibition_id)

    results = query.order_by(Artwork.id).all()
    
    # ArtworkResponse 형식으로 변환
    artworks = []
    for artwork, artist_name, reaction_count in results:
        artworks.append({
            "id": artwork.id,
            "title": artwork.title,
            "artist_id": artwork.artist_id,
            "artist_name": artist_name,
            "description": artwork.description,
            "year": artwork.year,
            "thumbnail_url": artwork.thumbnail_url,
            "reaction_count": reaction_count,
            "created_at": artwork.created_at,
            "updated_at": artwork.updated_at,
        })
    
    return artworks


@router.get(
    "/{artwork_id}",
    response_model=ArtworkDetail,
    summary="작품 상세 조회",
    description="작품 ID로 상세 정보를 조회합니다. 작가 및 전시 정보 포함.",
)
def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """
    작품 상세 조회 (전체 정보)
    
    Args:
        artwork_id: 작품 ID
        
    Returns:
        ArtworkDetail: 작품 상세 정보 (artist, exhibitions, reaction_count 포함)
        
    Raises:
        404: 작품을 찾을 수 없음
    """
    # 작품 조회 (관계 데이터 포함)
    artwork = (
        db.query(Artwork)
        .options(
            joinedload(Artwork.artist),
            joinedload(Artwork.exhibitions).joinedload(Exhibition.venue),
            joinedload(Artwork.reactions)
        )
        .filter(Artwork.id == artwork_id)
        .first()
    )
    
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )
    
    # ArtworkDetail 형식으로 변환
    result = {
        "id": artwork.id,
        "title": artwork.title,
        "artist_id": artwork.artist_id,
        "artist": artwork.artist,
        "description": artwork.description,
        "year": artwork.year,
        "thumbnail_url": artwork.thumbnail_url,
        "reaction_count": len(artwork.reactions),
        "exhibitions": [
            {
                "id": ex.id,
                "title": ex.title,
                "venue_name": ex.venue.name if ex.venue else "",
                "start_date": ex.start_date,
                "end_date": ex.end_date,
                "cover_image_url": ex.cover_image_url,
            }
            for ex in artwork.exhibitions
        ],
        "created_at": artwork.created_at,
        "updated_at": artwork.updated_at,
    }
    
    return result


@router.post(
    "",
    response_model=ArtworkDetail,
    status_code=status.HTTP_201_CREATED,
    summary="작품 생성",
    description="새 작품을 등록합니다. (관리자 전용, API Key 필요)",
)
def create_artwork(
    artwork_data: ArtworkCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    작품 생성 (관리자)

    Args:
        artwork_data: 작품 생성 데이터
        
    Returns:
        ArtworkDetail: 생성된 작품 정보 (작가, 전시 포함)

    Raises:
        404: 존재하지 않는 artist_id
    """
    # Artist 존재 여부 확인
    artist = db.query(Artist).filter(Artist.id == artwork_data.artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작가 ID {artwork_data.artist_id}를 찾을 수 없습니다",
        )

    new_artwork = Artwork(**artwork_data.model_dump())
    db.add(new_artwork)
    db.commit()
    db.refresh(new_artwork)
    
    # 생성 후 상세 정보 조회하여 반환
    return get_artwork(new_artwork.id, db)


@router.put(
    "/{artwork_id}",
    response_model=ArtworkDetail,
    summary="작품 수정",
    description="작품 정보를 수정합니다. (관리자 전용, API Key 필요)",
)
def update_artwork(
    artwork_id: int,
    artwork_data: ArtworkUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    작품 정보 수정 (관리자)
    
    Args:
        artwork_id: 작품 ID
        artwork_data: 수정 데이터

    Returns:
        ArtworkDetail: 수정된 작품 정보 (작가, 전시 포함)
        
    Raises:
        404: 작품 또는 작가를 찾을 수 없음
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )

    # Artist 존재 여부 확인
    if artwork_data.artist_id:
        artist = db.query(Artist).filter(Artist.id == artwork_data.artist_id).first()
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작가 ID {artwork_data.artist_id}를 찾을 수 없습니다",
            )

    update_data = artwork_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(artwork, key, value)

    db.commit()
    db.refresh(artwork)
    
    # 수정 후 상세 정보 조회하여 반환
    return get_artwork(artwork_id, db)


@router.delete(
    "/{artwork_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="작품 삭제",
    description="작품을 삭제합니다. (관리자 전용, API Key 필요)",
)
def delete_artwork(
    artwork_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    작품 삭제 (관리자)
    
    Args:
        artwork_id: 작품 ID
        
    Raises:
        404: 작품을 찾을 수 없음
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )

    db.delete(artwork)
    db.commit()
    return None


def resize_base64_image(base64_string: str, max_size: int = 1024) -> str:
    """
    base64 이미지를 리사이즈하여 크기 줄이기
    
    Args:
        base64_string: base64 인코딩된 이미지
        max_size: 최대 가로/세로 크기 (px)
        
    Returns:
        str: 리사이즈된 base64 이미지
    """
    try:
        # base64 → 이미지
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # RGB로 변환 (RGBA면)
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")
        
        # 리사이즈 (비율 유지)
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # 이미지 → base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        resized_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return resized_base64
        
    except Exception as e:
        logger.error(f"이미지 리사이즈 오류: {e}")
        raise


@router.post(
    "/match",
    response_model=ArtworkMatchResponse,
    summary="작품 이미지 매칭",
    description="업로드된 이미지와 유사한 작품을 전체 작품에서 찾습니다. Lambda를 통해 이미지 매칭 수행.",
)
async def match_artwork(request: ArtworkMatchRequest, db: Session = Depends(get_db)):
    try:
        # 0. 이미지 리사이즈 (크기 줄이기)
        logger.info("업로드 이미지 리사이즈 시작")
        resized_image = resize_base64_image(
            request.image_base64, 
            max_size=1024  # 1024x1024 이하로
        )
        original_size = len(request.image_base64) / 1024 / 1024
        resized_size = len(resized_image) / 1024 / 1024
        logger.info(f"이미지 크기: {original_size:.2f}MB → {resized_size:.2f}MB")
        
        # 1. 전체 작품 조회
        artworks = (
            db.query(Artwork)
            .options(
                joinedload(Artwork.artist),
                joinedload(Artwork.exhibitions).joinedload(Exhibition.venue)
            )
            .all()
        )

        if not artworks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록된 작품이 없습니다",
            )

        logger.info(f"전체 작품 {len(artworks)}개와 매칭 시작")

        # 2. 배치 처리
        BATCH_SIZE = 50  # 이미지 작아졌으니 배치 크기 증가
        all_results = []
        
        for i in range(0, len(artworks), BATCH_SIZE):
            batch = artworks[i:i + BATCH_SIZE]
            
            artwork_list = [
                {
                    "id": artwork.id,
                    "title": artwork.title,
                    "artist_id": artwork.artist_id,
                    "artist_name": artwork.artist.name if artwork.artist else "",
                    "thumbnail_url": artwork.thumbnail_url,
                }
                for artwork in batch
            ]
            
            batch_num = i // BATCH_SIZE + 1
            total_batches = (len(artworks) + BATCH_SIZE - 1) // BATCH_SIZE
            logger.info(f"배치 {batch_num}/{total_batches}: {len(artwork_list)}개 작품 매칭")
            
            try:
                batch_result = lambda_client.invoke_image_matching(
                    image_base64=resized_image,  # ✅ 리사이즈된 이미지 사용
                    artworks=artwork_list,
                    threshold=request.threshold,
                )
                
                if batch_result.get("results"):
                    all_results.extend(batch_result["results"])
                    logger.info(f"배치 {batch_num}: {len(batch_result['results'])}개 매칭됨")
                    
            except Exception as e:
                logger.error(f"배치 {batch_num} 매칭 오류: {e}")
                continue
        
        logger.info(f"전체 배치 완료: 총 {len(all_results)}개 매칭됨")
        
        # 3. 결과에 전시 정보 추가
        artwork_dict = {artwork.id: artwork for artwork in artworks}
        
        enhanced_results = []
        for result in all_results:
            artwork = artwork_dict.get(result["artwork_id"])
            if artwork:
                enhanced_results.append({
                    "artwork_id": result["artwork_id"],
                    "title": result["title"],
                    "artist_id": result["artist_id"],
                    "artist_name": result["artist_name"],
                    "thumbnail_url": result.get("thumbnail_url"),
                    "similarity": result["similarity"],
                    "exhibitions": [
                        {
                            "id": ex.id,
                            "title": ex.title,
                            "venue_name": ex.venue.name if ex.venue else "",
                            "start_date": ex.start_date,
                            "end_date": ex.end_date,
                            "cover_image_url": ex.cover_image_url,
                        }
                        for ex in artwork.exhibitions
                    ]
                })
        
        # 4. 유사도 높은 순 정렬
        enhanced_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        logger.info(f"매칭 완료: 총 {len(enhanced_results)}개 작품 발견")
        
        return {
            "matched": len(enhanced_results) > 0,
            "total_matches": len(enhanced_results),
            "threshold": request.threshold,
            "results": enhanced_results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"이미지 매칭 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 매칭 중 오류가 발생했습니다: {str(e)}",
        )