# app/api/v1/endpoints/artworks.py
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artist import Artist
from app.models.artwork import Artwork
from app.models.exhibition import Exhibition
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


@router.get("", response_model=List[ArtworkResponse])
def get_artworks(
    artist_id: Optional[int] = Query(None, description="작가 ID"),
    exhibition_id: Optional[int] = Query(None, description="전시 ID"),
    db: Session = Depends(get_db),
):
    """
    작품 전체 조회

    Args:
        artist_id: 작가 ID로 필터링
        exhibition_id: 전시 ID로 필터링

    Returns:
        List[ArtworkResponse]: 작품 목록

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

    query = db.query(Artwork)

    if artist_id:
        query = query.filter(Artwork.artist_id == artist_id)

    if exhibition_id:
        query = query.join(Artwork.exhibitions).filter(Exhibition.id == exhibition_id)

    artworks = query.order_by(Artwork.id).all()
    return artworks


@router.get("/{artwork_id}", response_model=ArtworkDetail)
def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """
    작품 상세 조회 (작가, 전시 정보 포함)
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )
    return artwork


@router.post("", response_model=ArtworkDetail, status_code=status.HTTP_201_CREATED)
def create_artwork(artwork_data: ArtworkCreate, db: Session = Depends(get_db)):
    """
    작품 생성 (관리자)

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
    return new_artwork


@router.put("/{artwork_id}", response_model=ArtworkDetail)
def update_artwork(
    artwork_id: int, artwork_data: ArtworkUpdate, db: Session = Depends(get_db)
):
    """
    작품 정보 수정 (관리자)

    Returns:
        ArtworkDetail: 수정된 작품 정보 (작가, 전시 포함)
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
    return artwork


@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """
    작품 삭제 (관리자)
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


@router.post("/match", response_model=ArtworkMatchResponse, summary="작품 이미지 매칭")
async def match_artwork(request: ArtworkMatchRequest, db: Session = Depends(get_db)):
    """
    업로드된 이미지와 유사한 작품을 찾는다.

    - **image_base64**: Base64 인코딩된 이미지
    - **exhibition_id**: 전시 ID
    - **threshold**: 유사도 임계값 (0.0 ~ 1.0)
    """
    try:
        # 1. 전시 조회
        exhibition = (
            db.query(Exhibition).filter(Exhibition.id == request.exhibition_id).first()
        )

        if not exhibition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"전시 ID {request.exhibition_id}를 찾을 수 없습니다",
            )

        # 2. 해당 전시의 작품들 조회 (relationship을 통해)
        artworks = exhibition.artworks

        if not artworks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"전시 ID {request.exhibition_id}에 작품이 없습니다",
            )

        # 3. Lambda에 전달할 작품 정보 구성
        artwork_list = [
            {
                "id": artwork.id,
                "title": artwork.title,
                "artist_id": artwork.artist_id,
                "thumbnail_url": artwork.thumbnail_url,
            }
            for artwork in artworks
        ]

        logger.info(f"전시 {request.exhibition_id}의 작품 {len(artwork_list)}개와 매칭")

        # 4. Lambda 호출
        result = lambda_client.invoke_image_matching(
            image_base64=request.image_base64,
            artworks=artwork_list,
            threshold=request.threshold,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"이미지 매칭 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 매칭 중 오류가 발생했습니다: {str(e)}",
        )
