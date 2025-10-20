# app/api/v1/endpoints/visitors.py
from typing import List

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.visitor import Visitor
from app.schemas.visitor import VisitorCreate, VisitorResponse, VisitorUpdate
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/visitors", tags=["Visitors"])


@router.get(
    "",
    response_model=List[VisitorResponse],
    summary="관람객 목록 조회",
    description="관람객 목록을 조회합니다.",
)
def get_visitors(db: Session = Depends(get_db)):
    """
    관람객 전체 조회 (관리자)

    Returns:
        List[VisitorResponse]: 관람객 목록
    """
    visitors = db.query(Visitor).order_by(Visitor.id).all()
    return visitors


@router.get(
    "/{visitor_id}",
    response_model=VisitorResponse,
    summary="관람객 상세 조회",
    description="관람객 ID로 상세 정보를 조회합니다.",
)
def get_visitor(visitor_id: int, db: Session = Depends(get_db)):
    """
    관람객 상세 조회

    Args:
        visitor_id: 관람객 ID

    Returns:
        VisitorResponse: 관람객 정보

    Raises:
        404: 관람객을 찾을 수 없음
    """
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 ID {visitor_id}를 찾을 수 없습니다",
        )
    return visitor


@router.get(
    "/uuid/{uuid}", 
    response_model=VisitorResponse,
    summary="UUID로 관람객 조회",
    description="iOS UUID로 관람객 정보를 조회합니다.",
)
def get_visitor_by_uuid(uuid: str, db: Session = Depends(get_db)):
    """
    관람객 UUID로 조회

    Args:
        uuid: iOS에서 생성한 UUID

    Returns:
        VisitorResponse: 관람객 정보

    Raises:
        404: 관람객을 찾을 수 없음
    """
    visitor = db.query(Visitor).filter(Visitor.uuid == uuid).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 UUID {uuid}를 찾을 수 없습니다",
        )
    return visitor


@router.post(
    "",
    response_model=VisitorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="관람객 생성",
    description="새 관람객을 생성합니다. UUID 중복 불가.",
)
def create_visitor(visitor_data: VisitorCreate, db: Session = Depends(get_db)):
    """
    관람객 생성

    Args:
        visitor_data: 관람객 생성 데이터 (uuid, name)

    Returns:
        VisitorResponse: 생성된 관람객 정보

    Raises:
        400: 중복된 UUID
    """
    # UUID 중복 체크
    existing = db.query(Visitor).filter(Visitor.uuid == visitor_data.uuid).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"관람객 UUID '{visitor_data.uuid}'이(가) 이미 존재합니다",
        )

    new_visitor = Visitor(**visitor_data.model_dump())
    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)
    return new_visitor


@router.put(
    "/{visitor_id}",
    response_model=VisitorResponse,
    summary="관람객 정보 수정",
    description="관람객 이름을 수정합니다.",
)
def update_visitor(
    visitor_id: int, visitor_data: VisitorUpdate, db: Session = Depends(get_db)
):
    """
    관람객 정보 수정

    Args:
        visitor_id: 관람객 ID
        visitor_data: 수정 데이터

    Returns:
        VisitorResponse: 수정된 관람객 정보

    Raises:
        404: 관람객을 찾을 수 없음
    """
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 ID {visitor_id}를 찾을 수 없습니다",
        )

    update_data = visitor_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(visitor, key, value)

    db.commit()
    db.refresh(visitor)
    return visitor


@router.delete(
    "/{visitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="관람객 삭제",
    description="관람객을 삭제합니다.",
)
def delete_visitor(visitor_id: int, db: Session = Depends(get_db)):
    """
    관람객 삭제 (관리자)

    Args:
        visitor_id: 관람객 ID

    Raises:
        404: 관람객을 찾을 수 없음
    """
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 ID {visitor_id}를 찾을 수 없습니다",
        )

    db.delete(visitor)
    db.commit()
    return None
