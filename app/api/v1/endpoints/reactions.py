# app/api/v1/endpoints/reactions.py
import json
import logging
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.artwork import Artwork
from app.models.reaction import Reaction
from app.models.tag import Tag
from app.models.visit_history import VisitHistory
from app.schemas.reaction import (
    ReactionDetail,
    ReactionResponse,
)
from app.utils.s3_client import s3_client
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)

router = APIRouter(prefix="/reactions", tags=["Reactions"])

logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=List[ReactionResponse],
    summary="반응 목록 조회",
    description="반응 목록을 조회합니다. artwork_id, visitor_id, visit_id로 필터링 가능합니다.",
)
def get_reactions(
    artwork_id: Optional[int] = Query(None, description="작품 ID로 필터링"),
    visitor_id: Optional[int] = Query(None, description="관람객 ID로 필터링"),
    visit_id: Optional[int] = Query(None, description="방문 기록 ID로 필터링"),
    db: Session = Depends(get_db),
):
    """
    반응 목록 조회 (가벼운 버전)

    Args:
        artwork_id: 작품 ID로 필터링
        visitor_id: 관람객 ID로 필터링
        visit_id: 방문 기록 ID로 필터링

    Returns:
        List[ReactionResponse]: 반응 목록 (artwork_title, visitor_name 포함)
    """
    query = db.query(Reaction).options(
        joinedload(Reaction.artwork),
        joinedload(Reaction.visitor),
        joinedload(Reaction.tags).joinedload(Tag.category),
    )

    # 필터링
    if artwork_id:
        query = query.filter(Reaction.artwork_id == artwork_id)
    if visitor_id:
        query = query.filter(Reaction.visitor_id == visitor_id)
    if visit_id:
        query = query.filter(Reaction.visit_id == visit_id)

    reactions = query.order_by(Reaction.created_at.desc()).all()

    # ReactionResponse 형식으로 변환
    result = []
    for reaction in reactions:
        result.append(
            {
                "id": reaction.id,
                "artwork_id": reaction.artwork_id,
                "artwork_title": reaction.artwork.title if reaction.artwork else "",
                "visitor_id": reaction.visitor_id,
                "visitor_name": reaction.visitor.name if reaction.visitor else None,
                "visit_id": reaction.visit_id,
                "comment": reaction.comment,
                "image_url": reaction.image_url,
                "tags": reaction.tags,
                "created_at": reaction.created_at,
                "updated_at": reaction.updated_at,
            }
        )

    return result


@router.get(
    "/{reaction_id}",
    response_model=ReactionDetail,
    summary="반응 상세 조회",
    description="반응 ID로 상세 정보를 조회합니다. 작품, 관람객, 방문 기록, 태그 전체 정보 포함.",
)
def get_reaction(reaction_id: int, db: Session = Depends(get_db)):
    """
    반응 상세 조회 (전체 정보)

    Args:
        reaction_id: 반응 ID

    Returns:
        ReactionDetail: 반응 상세 정보 (artwork, visitor, visit, tags 포함)

    Raises:
        404: 반응을 찾을 수 없음
    """
    reaction = (
        db.query(Reaction)
        .options(
            joinedload(Reaction.artwork).joinedload(Artwork.artist),
            joinedload(Reaction.visitor),
            joinedload(Reaction.visit).joinedload(VisitHistory.exhibition),
            joinedload(Reaction.tags).joinedload(Tag.category),
        )
        .filter(Reaction.id == reaction_id)
        .first()
    )

    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다",
        )

    # ReactionDetail 형식으로 변환
    result = {
        "id": reaction.id,
        "artwork_id": reaction.artwork_id,
        "artwork": (
            {
                "id": reaction.artwork.id,
                "title": reaction.artwork.title,
                "artist_id": reaction.artwork.artist_id,
                "artist_name": (
                    reaction.artwork.artist.name if reaction.artwork.artist else ""
                ),
                "description": reaction.artwork.description,
                "year": reaction.artwork.year,
                "thumbnail_url": reaction.artwork.thumbnail_url,
                "reaction_count": (
                    len(reaction.artwork.reactions) if reaction.artwork else 0
                ),
                "created_at": reaction.artwork.created_at,
                "updated_at": reaction.artwork.updated_at,
            }
            if reaction.artwork
            else None
        ),
        "visitor_id": reaction.visitor_id,
        "visitor": reaction.visitor,
        "visit_id": reaction.visit_id,
        "visit": (
            {
                "id": reaction.visit.id,
                "exhibition_id": reaction.visit.exhibition_id,
                "exhibition_title": (
                    reaction.visit.exhibition.title if reaction.visit.exhibition else ""
                ),
                "visited_at": reaction.visit.visited_at,
            }
            if reaction.visit
            else None
        ),
        "comment": reaction.comment,
        "image_url": reaction.image_url,
        "tags": reaction.tags,
        "created_at": reaction.created_at,
        "updated_at": reaction.updated_at,
    }

    return result


@router.post(
    "",
    response_model=ReactionDetail,
    status_code=status.HTTP_201_CREATED,
    summary="반응 생성",
    description="새 반응을 생성합니다. 이미지 업로드 및 태그 연결 포함.",
)
async def create_reaction(
    visitor_id: int = Form(...),
    artwork_id: int = Form(...),
    visit_id: Optional[int] = Form(None),
    comment: Optional[str] = Form(None),
    tag_ids: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    반응 생성 (이미지 포함)

    Args:
        visitor_id: 관람객 ID
        artwork_id: 작품 ID
        visit_id: 방문 기록 ID (선택)
        comment: 코멘트 (선택)
        tag_ids: 태그 ID 배열 JSON string (예: "[1,3,5]")
        image: 촬영한 이미지 파일

    Returns:
        ReactionDetail: 생성된 반응 정보 (작품, 관람객, 태그, 이미지 포함)

    Raises:
        404: 존재하지 않는 artwork_id, visitor_id, visit_id, tag_ids
        500: S3 업로드 실패

    Note:
        이미지는 S3 reactions 폴더에 저장됨
        visit_id가 있으면: reactions/{env}/exhibition_{id}/visitor_{id}_{timestamp}.jpg
        visit_id가 없으면: reactions/{uuid}.jpg
    """

    # Artwork 존재 여부 확인
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )

    # Visitor 존재 여부 확인
    from app.models.visitor import Visitor

    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 ID {visitor_id}를 찾을 수 없습니다",
        )

    # Visit 존재 여부 확인 (선택) & exhibition_id 추출
    exhibition_id = None
    if visit_id:
        visit = db.query(VisitHistory).filter(VisitHistory.id == visit_id).first()
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"방문 기록 ID {visit_id}를 찾을 수 없습니다",
            )
        exhibition_id = visit.exhibition_id
        logger.info(f"Exhibition ID 추출: {exhibition_id} (Visit ID: {visit_id})")

    # S3에 이미지 업로드
    try:
        image_url = await s3_client.upload_file(
            file=image,
            folder="reactions",
            exhibition_id=exhibition_id,  # visit_id가 있으면 전시 ID 전달
            visitor_id=visitor_id,  # 관람객 ID 전달
        )
        logger.info(f"S3 업로드 성공: {image_url}")
    except Exception as e:
        logger.error(f"S3 업로드 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 업로드 실패: {str(e)}",
        )

    # Reaction 생성
    new_reaction = Reaction(
        visitor_id=visitor_id,
        artwork_id=artwork_id,
        visit_id=visit_id,
        comment=comment,
        image_url=image_url,
    )
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)

    # Tag 연결 (M:N)
    if tag_ids:
        try:
            tag_id_list = json.loads(tag_ids)
            tags = db.query(Tag).filter(Tag.id.in_(tag_id_list)).all()

            # 존재하지 않는 태그 확인
            found_ids = {tag.id for tag in tags}
            missing_ids = set(tag_id_list) - found_ids
            if missing_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"태그 ID {sorted(missing_ids)}를 찾을 수 없습니다",
                )

            new_reaction.tags.extend(tags)
            db.commit()
            db.refresh(new_reaction)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tag_ids는 유효한 JSON 배열 문자열이어야 합니다",
            )

    # 생성 후 상세 정보 조회하여 반환
    return get_reaction(new_reaction.id, db)


@router.put(
    "/{reaction_id}",
    response_model=ReactionDetail,
    summary="반응 수정",
    description="반응의 코멘트, 이미지, 태그를 수정합니다. 이미지 수정 시 기존 S3 이미지는 삭제됩니다.",
)
async def update_reaction(
    reaction_id: int,
    comment: Optional[str] = Form(None),
    tag_ids: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    반응 수정 (이미지 교체 포함)

    Args:
        reaction_id: 반응 ID
        comment: 코멘트 (선택)
        tag_ids: 태그 ID 배열 JSON string (예: "[1,3,5]") (선택)
        image: 새 이미지 파일 (선택)

    Returns:
        ReactionDetail: 수정된 반응 정보 (전체)

    Raises:
        404: 반응을 찾을 수 없음
        400: comment와 tag_ids 둘 다 비움

    Note:
        - 이미지를 새로 업로드하면 기존 S3 이미지는 자동 삭제됩니다
        - tag_ids는 JSON 배열 문자열로 전달 (예: "[1,2,3]")
    """
    reaction = (
        db.query(Reaction)
        .options(joinedload(Reaction.visit))
        .filter(Reaction.id == reaction_id)
        .first()
    )

    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다",
        )

    # comment 수정
    if comment is not None:
        reaction.comment = comment  # type: ignore

    # image 수정 (새 이미지 업로드 시)
    if image is not None:
        # 기존 S3 이미지 삭제
        old_image_url = reaction.image_url
        if old_image_url:
            try:
                s3_client.delete_file(str(old_image_url))
                logger.info(f"기존 이미지 삭제 성공: {old_image_url}")
            except Exception as e:
                logger.warning(f"기존 이미지 삭제 실패 (계속 진행): {e}")

        # 새 이미지 업로드
        try:
            # visit 정보로부터 exhibition_id 추출
            exhibition_id = None
            if reaction.visit:
                exhibition_id = reaction.visit.exhibition_id

            new_image_url = await s3_client.upload_file(
                file=image,
                folder="reactions",
                exhibition_id=exhibition_id,
                visitor_id=reaction.visitor_id,
            )
            reaction.image_url = new_image_url  # type: ignore
            logger.info(f"새 이미지 업로드 성공: {new_image_url}")
        except Exception as e:
            logger.error(f"S3 업로드 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 실패: {str(e)}",
            )

    # tag_ids 수정
    if tag_ids is not None:
        try:
            # 기존 태그 삭제
            reaction.tags.clear()

            # 새 태그 추가
            if tag_ids:
                tag_id_list = json.loads(tag_ids)
                tags = db.query(Tag).filter(Tag.id.in_(tag_id_list)).all()

                # 존재하지 않는 태그 체크
                found_ids = {tag.id for tag in tags}
                missing_ids = set(tag_id_list) - found_ids
                if missing_ids:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"태그 ID {sorted(missing_ids)}를 찾을 수 없습니다",
                    )

                reaction.tags.extend(tags)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tag_ids는 유효한 JSON 배열 문자열이어야 합니다",
            )

    # Validation: comment와 tag_ids 둘 다 비어있으면 에러
    if not reaction.comment and not reaction.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="코멘트 또는 태그 중 하나는 필수입니다",
        )

    db.commit()
    db.refresh(reaction)

    # 수정 후 상세 정보 조회하여 반환
    return get_reaction(reaction_id, db)


@router.delete(
    "/{reaction_id}",
    status_code=204,
    summary="반응 삭제",
    description="반응을 삭제합니다. 연결된 S3 이미지도 함께 삭제됩니다.",
)
async def delete_reaction(reaction_id: int, db: Session = Depends(get_db)):
    """
    반응 삭제 (촬영한 이미지도 함께 삭제)

    Args:
        reaction_id: 반응 ID

    Raises:
        404: 반응을 찾을 수 없음

    Note:
        S3에 저장된 이미지도 함께 삭제됩니다
    """
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="반응을 찾을 수 없습니다"
        )

    # S3에서 이미지 삭제 (있는 경우)
    if reaction.image_url:
        try:
            s3_client.delete_file(str(reaction.image_url))
            logger.info(f"S3 이미지 삭제 성공: {reaction.image_url}")
        except Exception as e:
            logger.warning(f"S3 이미지 삭제 실패 (계속 진행): {e}")

    # DB에서 반응 삭제
    db.delete(reaction)
    db.commit()

    logger.info(f"Reaction ID {reaction_id} 삭제 완료")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
