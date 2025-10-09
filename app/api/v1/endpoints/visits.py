from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.visit_history import VisitHistory
from app.models.user import User
from app.models.exhibition import Exhibition
from app.models.review import Review
from app.models.artwork import Artwork
from app.schemas.visit_history import VisitHistoryCreate, VisitHistoryResponse

router = APIRouter()


@router.post("/", response_model=VisitHistoryResponse, status_code=201)
async def create_visit(
    visit: VisitHistoryCreate,
    db: Session = Depends(get_db)
):
    """
    전시 방문 기록 생성
    관람객이 전시를 시작할 때 호출
    """
    # 사용자 확인
    user = db.query(User).filter(User.id == visit.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 전시 확인
    exhibition = db.query(Exhibition).filter(Exhibition.id == visit.exhibition_id).first()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    # 중복 방문 확인 (같은 날 같은 전시)
    today = datetime.now().date()
    existing_visit = db.query(VisitHistory).filter(
        VisitHistory.user_id == visit.user_id,
        VisitHistory.exhibition_id == visit.exhibition_id,
        func.date(VisitHistory.visited_at) == today
    ).first()
    
    if existing_visit:
        # 이미 오늘 방문 기록이 있으면 그걸 반환
        return existing_visit
    
    # 방문 기록 생성
    db_visit = VisitHistory(**visit.model_dump())
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit


@router.get("/user/{user_id}", response_model=List[dict])
async def get_user_visits(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 사용자의 관람 이력 조회
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    visits = db.query(VisitHistory).filter(VisitHistory.user_id == user_id).all()
    
    # 전시 정보 포함해서 반환
    response_data = []
    for visit in visits:
        exhibition = db.query(Exhibition).filter(Exhibition.id == visit.exhibition_id).first()
        response_data.append({
            "id": visit.id,
            "user_id": visit.user_id,
            "exhibition_id": visit.exhibition_id,
            "visited_at": visit.visited_at,
            "exhibition": {
                "id": exhibition.id,
                "title": exhibition.title,
                "location": exhibition.location,
                "poster_url": exhibition.poster_url,
                "start_date": exhibition.start_date,
                "end_date": exhibition.end_date
            }
        })
    
    return response_data


@router.get("/{visit_id}/artworks", response_model=List[dict])
async def get_visit_artworks(
    visit_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 방문에서 본 작품들 조회
    (해당 전시에서 사용자가 리뷰 남긴 작품들)
    """
    visit = db.query(VisitHistory).filter(VisitHistory.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    # 해당 전시에서 이 사용자가 리뷰 남긴 작품들
    reviews = db.query(Review).join(Artwork).filter(
        Review.user_id == visit.user_id,
        Artwork.exhibition_id == visit.exhibition_id
    ).all()
    
    # 작품 정보와 리뷰 정보 함께 반환
    response_data = []
    for review in reviews:
        artwork = db.query(Artwork).filter(Artwork.id == review.artwork_id).first()
        response_data.append({
            "artwork": {
                "id": artwork.id,
                "title": artwork.title,
                "artist_name": artwork.artist_name,
                "image_url": artwork.image_url,
                "year": artwork.year
            },
            "review": {
                "id": review.id,
                "photo_url": review.photo_url,
                "text_review": review.text_review,
                "tags": [{"id": tag.id, "name": tag.name} for tag in review.tags],
                "created_at": review.created_at
            }
        })
    
    return response_data