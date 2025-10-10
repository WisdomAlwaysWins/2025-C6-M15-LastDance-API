from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, any_
from typing import List
from collections import Counter

from app.database import get_db
from app.models.user import User, UserType
from app.models.exhibition import Exhibition
from app.models.artwork import Artwork
from app.models.reaction import Review

router = APIRouter()


@router.get("/exhibitions")
async def get_artist_exhibitions(
    artist_name: str,
    db: Session = Depends(get_db)
):
    """
    특정 작가가 참여한 전시 목록 조회
    artist_name으로 검색 (Exhibition.artist_names 배열에서)
    """
    # artist_names 배열에 해당 작가 이름이 포함된 전시들 조회
    exhibitions = db.query(Exhibition).filter(
        Exhibition.artist_names.any(artist_name)
    ).all()
    
    if not exhibitions:
        return []
    
    # 전시 정보와 작가의 작품 수 포함
    response_data = []
    for exhibition in exhibitions:
        # 이 전시에서 해당 작가의 작품 수
        artwork_count = db.query(Artwork).filter(
            Artwork.exhibition_id == exhibition.id,
            Artwork.artist_name == artist_name
        ).count()
        
        response_data.append({
            "id": exhibition.id,
            "title": exhibition.title,
            "description": exhibition.description,
            "location": exhibition.location,
            "poster_url": exhibition.poster_url,
            "start_date": exhibition.start_date,
            "end_date": exhibition.end_date,
            "my_artwork_count": artwork_count
        })
    
    return response_data


@router.get("/artworks")
async def get_artist_artworks(
    artist_name: str,
    exhibition_id: int = None,
    db: Session = Depends(get_db)
):
    """
    작가의 작품 목록 조회
    exhibition_id가 있으면 해당 전시의 작품만, 없으면 모든 작품
    """
    query = db.query(Artwork).filter(Artwork.artist_name == artist_name)
    
    if exhibition_id:
        query = query.filter(Artwork.exhibition_id == exhibition_id)
    
    artworks = query.all()
    
    # 각 작품의 리뷰 개수 포함
    response_data = []
    for artwork in artworks:
        review_count = db.query(Review).filter(Review.artwork_id == artwork.id).count()
        
        response_data.append({
            "id": artwork.id,
            "title": artwork.title,
            "artist_name": artwork.artist_name,
            "description": artwork.description,
            "year": artwork.year,
            "image_url": artwork.image_url,
            "exhibition_id": artwork.exhibition_id,
            "review_count": review_count
        })
    
    return response_data


@router.get("/artworks/{artwork_id}/reviews/statistics")
async def get_artwork_review_statistics(
    artwork_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 작품의 평가 통계
    - 태그별 카운트
    - 텍스트 리뷰 목록
    - 총 리뷰 수
    """
    # 작품 확인
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # 모든 리뷰 조회
    reviews = db.query(Review).filter(Review.artwork_id == artwork_id).all()
    
    if not reviews:
        return {
            "artwork": {
                "id": artwork.id,
                "title": artwork.title,
                "artist_name": artwork.artist_name,
                "image_url": artwork.image_url
            },
            "total_reviews": 0,
            "tag_statistics": [],
            "text_reviews": []
        }
    
    # 태그 통계 (모든 리뷰의 태그 카운트)
    all_tags = []
    for review in reviews:
        for tag in review.tags:
            all_tags.append(tag.name)
    
    tag_counter = Counter(all_tags)
    tag_statistics = [
        {"tag_name": tag, "count": count}
        for tag, count in tag_counter.most_common()
    ]
    
    # 텍스트 리뷰 목록 (텍스트가 있는 것만)
    text_reviews = []
    for review in reviews:
        if review.text_review:
            text_reviews.append({
                "id": review.id,
                "text": review.text_review,
                "photo_url": review.photo_url,
                "tags": [tag.name for tag in review.tags],
                "created_at": review.created_at
            })
    
    return {
        "artwork": {
            "id": artwork.id,
            "title": artwork.title,
            "artist_name": artwork.artist_name,
            "image_url": artwork.image_url
        },
        "total_reviews": len(reviews),
        "tag_statistics": tag_statistics,
        "text_reviews": text_reviews
    }