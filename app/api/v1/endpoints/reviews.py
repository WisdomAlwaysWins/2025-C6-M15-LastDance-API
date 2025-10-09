from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.models.review import Review
from app.models.artwork import Artwork
from app.models.tag import Tag
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.utils.s3_client import s3_client

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    image: UploadFile = File(...),
    artwork_id: int = Form(...),
    user_id: int = Form(...),
    text_review: Optional[str] = Form(None),
    tag_ids: str = Form("[]"),
    db: Session = Depends(get_db)
):
    """
    작품 평가 등록 (이미지 업로드 포함)
    
    Phase 1 (현재): 사용자가 작품 선택
    Phase 2 (나중): CLIP으로 자동 인식된 작품
    """
    # 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 작품 확인
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # 1. 이미지 S3 업로드
    file_content = await image.read()
    file_extension = image.filename.split(".")[-1]
    
    photo_url = s3_client.upload_file(
        file_content=file_content,
        file_extension=file_extension,
        folder="reviews"
    )
    
    if not photo_url:
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")
    
    # 2. tag_ids JSON 파싱
    try:
        tag_ids_list = json.loads(tag_ids)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="tag_ids must be a valid JSON array")
    
    # 3. 리뷰 생성
    db_review = Review(
        photo_url=photo_url,
        text_review=text_review,
        user_id=user_id,
        artwork_id=artwork_id
    )
    
    # 4. 태그 추가
    if tag_ids_list:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids_list)).all()
        db_review.tags = tags
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # 5. 응답 데이터 구성
    response_data = {
        "id": db_review.id,
        "photo_url": db_review.photo_url,
        "text_review": db_review.text_review,
        "artwork_id": db_review.artwork_id,
        "user_id": db_review.user_id,
        "tags": [{"id": tag.id, "name": tag.name} for tag in db_review.tags],
        "created_at": db_review.created_at
    }
    
    return response_data


@router.get("/artwork/{artwork_id}", response_model=List[ReviewResponse])
async def list_reviews_by_artwork(
    artwork_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 작품의 평가 목록 조회
    """
    # 작품 확인
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    reviews = db.query(Review).filter(Review.artwork_id == artwork_id).all()
    
    # 응답 데이터 구성
    response_data = []
    for review in reviews:
        response_data.append({
            "id": review.id,
            "photo_url": review.photo_url,
            "text_review": review.text_review,
            "artwork_id": review.artwork_id,
            "user_id": review.user_id,
            "tags": [{"id": tag.id, "name": tag.name} for tag in review.tags],
            "created_at": review.created_at
        })
    
    return response_data


@router.delete("/image", status_code=204)
async def delete_uploaded_image(
    photo_url: str = Form(...)
):
    """
    업로드한 이미지 삭제 (리뷰 등록 전 취소 시)
    iOS에서 뒤로가기 또는 취소 버튼 눌렀을 때 호출
    """
    success = s3_client.delete_file(photo_url)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete image from S3")
    
    return None