# app/api/v1/endpoints/visit_histories.py
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.exhibition import Exhibition
from app.models.reaction import Reaction
from app.models.visit_history import VisitHistory
from app.models.visitor import Visitor
from app.schemas.visit_history import (
    VisitHistoryCreate,
    VisitHistoryDetail,
    VisitHistoryResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

router = APIRouter(prefix="/visit-histories", tags=["Visit Histories"])


@router.post(
    "",
    response_model=VisitHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="방문 기록 생성",
    description="새 방문 기록을 생성합니다.",
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

    # 생성 후 상세 정보 조회하여 반환 (Response 형식)
    return get_visit_history_response(new_visit.id, db)


@router.get(
    "",
    response_model=List[VisitHistoryResponse],
    summary="방문 기록 목록 조회",
    description="방문 기록 목록을 조회합니다. visitor_id와 exhibition_id로 필터링 가능합니다.",
)
def get_visit_histories(
    visitor_id: Optional[int] = Query(None, description="관람객 ID로 필터링"),
    exhibition_id: Optional[int] = Query(None, description="전시 ID로 필터링"),
    db: Session = Depends(get_db),
):
    """
    방문 기록 목록 조회 (가벼운 버전)

    Args:
        visitor_id: 관람객 ID로 필터링
        exhibition_id: 전시 ID로 필터링

    Returns:
        List[VisitHistoryResponse]: 방문 기록 목록 (visitor_name, exhibition_title, reaction_count 포함)
    """
    # 쿼리 구성 (visitor, exhibition, reaction_count join)
    query = (
        db.query(
            VisitHistory,
            Visitor.name.label("visitor_name"),
            Exhibition.title.label("exhibition_title"),
            func.count(Reaction.id).label("reaction_count"),
        )
        .join(Visitor, VisitHistory.visitor_id == Visitor.id)
        .join(Exhibition, VisitHistory.exhibition_id == Exhibition.id)
        .outerjoin(Reaction, VisitHistory.id == Reaction.visit_id)
        .group_by(VisitHistory.id, Visitor.name, Exhibition.title)
    )

    if visitor_id:
        query = query.filter(VisitHistory.visitor_id == visitor_id)
    if exhibition_id:
        query = query.filter(VisitHistory.exhibition_id == exhibition_id)

    results = query.order_by(VisitHistory.visited_at.desc()).all()

    # VisitHistoryResponse 형식으로 변환
    visits = []
    for visit, visitor_name, exhibition_title, reaction_count in results:
        visits.append(
            {
                "id": visit.id,
                "visitor_id": visit.visitor_id,
                "visitor_name": visitor_name,
                "exhibition_id": visit.exhibition_id,
                "exhibition_title": exhibition_title,
                "visited_at": visit.visited_at,
                "reaction_count": reaction_count,
            }
        )

    return visits


@router.get(
    "/{visit_id}",
    response_model=VisitHistoryDetail,
    summary="방문 기록 상세 조회",
    description="방문 기록 ID로 상세 정보를 조회합니다. 전시 정보 및 반응 목록 포함.",
)
def get_visit_history(visit_id: int, db: Session = Depends(get_db)):
    """
    방문 기록 상세 조회 (전체 정보)

    Args:
        visit_id: 방문 기록 ID

    Returns:
        VisitHistoryDetail: 방문 기록 상세 (exhibition, reactions 포함)

    Raises:
        404: 방문 기록을 찾을 수 없음
    """
    # 방문 기록 조회 (관계 데이터 포함)
    visit = (
        db.query(VisitHistory)
        .options(
            joinedload(VisitHistory.visitor),
            joinedload(VisitHistory.exhibition).joinedload(Exhibition.venue),
            joinedload(VisitHistory.reactions).joinedload(Reaction.artwork),
        )
        .filter(VisitHistory.id == visit_id)
        .first()
    )

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"방문 기록 ID {visit_id}를 찾을 수 없습니다",
        )

    # VisitHistoryDetail 형식으로 변환
    result = {
        "id": visit.id,
        "visitor_id": visit.visitor_id,
        "visitor_name": visit.visitor.name if visit.visitor else None,
        "exhibition_id": visit.exhibition_id,
        "exhibition": (
            {
                "id": visit.exhibition.id,
                "title": visit.exhibition.title,
                "venue_name": (
                    visit.exhibition.venue.name if visit.exhibition.venue else ""
                ),
                "start_date": visit.exhibition.start_date,
                "end_date": visit.exhibition.end_date,
                "cover_image_url": visit.exhibition.cover_image_url,
            }
            if visit.exhibition
            else None
        ),
        "visited_at": visit.visited_at,
        "reactions": [
            {
                "id": reaction.id,
                "artwork_id": reaction.artwork_id,
                "artwork_title": reaction.artwork.title if reaction.artwork else "",
                "comment": reaction.comment,
                "created_at": reaction.created_at,
            }
            for reaction in visit.reactions
        ],
    }

    return result


def get_visit_history_response(visit_id: int, db: Session) -> dict:
    """
    방문 기록 Response 형식으로 조회 (내부 헬퍼 함수)

    Args:
        visit_id: 방문 기록 ID
        db: 데이터베이스 세션

    Returns:
        dict: VisitHistoryResponse 형식
    """
    result = (
        db.query(
            VisitHistory,
            Visitor.name.label("visitor_name"),
            Exhibition.title.label("exhibition_title"),
            func.count(Reaction.id).label("reaction_count"),
        )
        .join(Visitor, VisitHistory.visitor_id == Visitor.id)
        .join(Exhibition, VisitHistory.exhibition_id == Exhibition.id)
        .outerjoin(Reaction, VisitHistory.id == Reaction.visit_id)
        .filter(VisitHistory.id == visit_id)
        .group_by(VisitHistory.id, Visitor.name, Exhibition.title)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"방문 기록 ID {visit_id}를 찾을 수 없습니다",
        )

    visit, visitor_name, exhibition_title, reaction_count = result

    return {
        "id": visit.id,
        "visitor_id": visit.visitor_id,
        "visitor_name": visitor_name,
        "exhibition_id": visit.exhibition_id,
        "exhibition_title": exhibition_title,
        "visited_at": visit.visited_at,
        "reaction_count": reaction_count,
    }
