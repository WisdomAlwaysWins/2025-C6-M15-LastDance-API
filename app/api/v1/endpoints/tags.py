# app/api/v1/endpoints/tags.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tag import Tag
from app.models.tag_category import TagCategory
from app.schemas.tag import TagCreate, TagDetail, TagResponse, TagUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, status

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=List[TagResponse])
def get_tags(
    category_id: Optional[int] = Query(None, description="카테고리 ID로 필터링"),
    db: Session = Depends(get_db),
):
    """
    태그 전체 조회 (이름순)

    Args:
        category_id: 카테고리 ID (선택)

    Returns:
        List[TagResponse]: 태그 목록

    Raises:
        404: 존재하지 않는 category_id
    """
    # Category 존재 여부 확인
    if category_id:
        category = db.query(TagCategory).filter(TagCategory.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TagCategory with id {category_id} not found",
            )

    query = db.query(Tag)
    if category_id:
        query = query.filter(Tag.category_id == category_id)

    tags = query.order_by(Tag.name).all()
    return tags


@router.get("/{tag_id}", response_model=TagDetail)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    태그 상세 조회 (카테고리 정보 포함)
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )
    return tag


@router.post("", response_model=TagDetail, status_code=status.HTTP_201_CREATED)
def create_tag(tag_data: TagCreate, db: Session = Depends(get_db)):
    """
    태그 생성 (관리자)

    Returns:
        TagDetail: 생성된 태그 정보 (카테고리 포함)

    Raises:
        400: 중복된 태그명
        404: 존재하지 않는 category_id
    """
    # Category 존재 여부 확인
    category = (
        db.query(TagCategory).filter(TagCategory.id == tag_data.category_id).first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TagCategory with id {tag_data.category_id} not found",
        )

    # 중복 체크
    existing = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_data.name}' already exists",
        )

    new_tag = Tag(**tag_data.model_dump())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


@router.put("/{tag_id}", response_model=TagDetail)
def update_tag(tag_id: int, tag_data: TagUpdate, db: Session = Depends(get_db)):
    """
    태그 수정 (관리자)

    Returns:
        TagDetail: 수정된 태그 정보 (카테고리 포함)
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Category 존재 여부 확인
    if tag_data.category_id:
        category = (
            db.query(TagCategory).filter(TagCategory.id == tag_data.category_id).first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TagCategory with id {tag_data.category_id} not found",
            )

    # 이름 중복 체크
    if tag_data.name:
        existing = (
            db.query(Tag).filter(Tag.name == tag_data.name, Tag.id != tag_id).first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_data.name}' already exists",
            )

    update_data = tag_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tag, key, value)

    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    태그 삭제 (관리자)
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    db.delete(tag)
    db.commit()
    return None
