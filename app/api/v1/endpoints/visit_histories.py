# app/api/v1/endpoints/visit_histories.py
from typing import List

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exhibition import Exhibition
from app.models.visit_history import VisitHistory
from app.models.visitor import Visitor
from app.schemas.visit_history import VisitHistoryCreate, VisitHistoryResponse
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/visit-histories", tags=["Visit Histories"])


@router.post(
    "", response_model=VisitHistoryResponse, status_code=status.HTTP_201_CREATED
)
def create_visit_history(visit_data: VisitHistoryCreate, db: Session = Depends(get_db)):
    """
    방문 기록 생성

    Args:
        visit_data: 방문 기록 생성 데이터

    Returns:
        VisitHistoryResponse: 생성된 방문 기록

    Raises:
        404: 존재하지 않는 visitor_id 또는 exhibition_id
    """
    # Visitor 존재 여부 확인
    visitor = db.query(Visitor).filter(Visitor.id == visit_data.visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 ID {visit_data.visitor_id}를 찾을 수 없습니다",
        )

    # Exhibition 존재 여부 확인
    exhibition = (
        db.query(Exhibition).filter(Exhibition.id == visit_data.exhibition_id).first()
    )
    if not exhibition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"전시 ID {visit_data.exhibition_id}를 찾을 수 없습니다",
        )

    # VisitHistory 생성
    new_visit = VisitHistory(**visit_data.model_dump())
    db.add(new_visit)
    db.commit()
    db.refresh(new_visit)

    return new_visit


@router.get("", response_model=List[VisitHistoryResponse])
def get_visit_histories(
    visitor_id: int = None, exhibition_id: int = None, db: Session = Depends(get_db)
):
    """
    방문 기록 조회

    Args:
        visitor_id: 관람객 ID로 필터링
        exhibition_id: 전시 ID로 필터링

    Returns:
        List[VisitHistoryResponse]: 방문 기록 목록
    """
    query = db.query(VisitHistory)

    if visitor_id:
        query = query.filter(VisitHistory.visitor_id == visitor_id)
    if exhibition_id:
        query = query.filter(VisitHistory.exhibition_id == exhibition_id)

    visits = query.order_by(VisitHistory.id).all()
    return visits


@router.get("/{visit_id}", response_model=VisitHistoryResponse)
def get_visit_history(visit_id: int, db: Session = Depends(get_db)):
    """
    방문 기록 상세 조회

    Args:
        visit_id: 방문 기록 ID

    Returns:
        VisitHistoryResponse: 방문 기록 상세

    Raises:
        404: 방문 기록을 찾을 수 없음
    """
    visit = db.query(VisitHistory).filter(VisitHistory.id == visit_id).first()
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"방문 기록 ID {visit_id}를 찾을 수 없습니다",
        )
    return visit
