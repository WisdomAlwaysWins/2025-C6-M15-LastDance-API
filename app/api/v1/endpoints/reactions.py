# app/api/v1/endpoints/reactions.py
import json
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artwork import Artwork
from app.models.reaction import Reaction
from app.models.tag import Tag
from app.models.visit_history import VisitHistory
from app.schemas.reaction import (  # ReactionCreate,
    ReactionDetail,
    ReactionResponse,
    ReactionUpdate,
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


@router.get("", response_model=List[ReactionResponse])
def get_reactions(
    artwork_id: Optional[int] = Query(None, description="작품 ID"),
    visitor_id: Optional[int] = Query(None, description="관람객 ID"),
    visit_id: Optional[int] = Query(None, description="방문 기록 ID"),
    db: Session = Depends(get_db),
):
    """
    반응 전체 조회

    Args:
        artwork_id: 작품 ID로 필터링
        visitor_id: 관람객 ID로 필터링
        visit_id: 방문 기록 ID로 필터링

    Returns:
        List[ReactionResponse]: 반응 목록
    """
    query = db.query(Reaction)

    # 필터링
    if artwork_id:
        query = query.filter(Reaction.artwork_id == artwork_id)
    if visitor_id:
        query = query.filter(Reaction.visitor_id == visitor_id)
    if visit_id:
        query = query.filter(Reaction.visit_id == visit_id)

    reactions = query.order_by(Reaction.created_at.desc()).all()
    return reactions


@router.get("/{reaction_id}", response_model=ReactionDetail)
def get_reaction(reaction_id: int, db: Session = Depends(get_db)):
    """
    반응 상세 조회 (작품, 관람객, 태그 포함)

    Args:
        reaction_id: 반응 ID

    Returns:
        ReactionDetail: 반응 상세 정보

    Raises:
        404: 반응을 찾을 수 없음
    """
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다",
        )
    return reaction


@router.post("", response_model=ReactionDetail, status_code=status.HTTP_201_CREATED)
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

    # Visit 존재 여부 확인 (선택)
    if visit_id:
        visit = db.query(VisitHistory).filter(VisitHistory.id == visit_id).first()
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"방문 기록 ID {visit_id}를 찾을 수 없습니다",
            )

    # S3에 이미지 업로드
    try:
        image_url = await s3_client.upload_file(file=image, folder="reactions")
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

    return new_reaction


@router.put("/{reaction_id}", response_model=ReactionResponse)
def update_reaction(
    reaction_id: int, reaction_data: ReactionUpdate, db: Session = Depends(get_db)
):
    """
    반응 수정

    Args:
        reaction_id: 반응 ID
        reaction_data: 수정 데이터

    Returns:
        ReactionResponse: 수정된 반응 정보

    Raises:
        404: 반응을 찾을 수 없음
        400: comment와 tag_ids 둘 다 비움
    """
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다",
        )

    # comment 수정
    if reaction_data.comment is not None:
        reaction.comment = reaction_data.comment  # type: ignore

    # tag_ids 수정
    if reaction_data.tag_ids is not None:
        # 기존 태그 삭제
        reaction.tags.clear()

        # 새 태그 추가
        if reaction_data.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(reaction_data.tag_ids)).all()

            # 존재하지 않는 태그 체크
            if len(tags) != len(reaction_data.tag_ids):
                found_ids = {tag.id for tag in tags}
                missing_ids = set(reaction_data.tag_ids) - found_ids
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"태그 ID {missing_ids}를 찾을 수 없습니다",
                )

            reaction.tags.extend(tags)

    # Validation: comment와 tag_ids 둘 다 비어있으면 에러
    if not reaction.comment and not reaction.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="코멘트 또는 태그 중 하나는 필수입니다",
        )

    db.commit()
    db.refresh(reaction)
    return reaction


@router.delete("/{reaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reaction(reaction_id: int, db: Session = Depends(get_db)):
    """
    반응 삭제 (촬영한 이미지도 함께 삭제)
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
        except Exception as e:
            logger.warning(f"S3 이미지 삭제 실패 (계속 진행): {e}")

    # DB에서 반응 삭제
    db.delete(reaction)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
