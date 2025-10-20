# app/api/v1/endpoints/tag_categories.py
from typing import List

from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.database import get_db
from app.models.tag_category import TagCategory
from app.schemas.tag_category import (
    TagCategoryCreate,
    TagCategoryDetail,
    TagCategoryResponse,
    TagCategoryUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/tag-categories", tags=["Tag Categories"])


@router.get("", response_model=List[TagCategoryResponse])
def get_tag_categories(db: Session = Depends(get_db)):
    """
    태그 카테고리 전체 조회 (ID 순)

    Returns:
        List[TagCategoryResponse]: 태그 카테고리 목록
    """
    categories = db.query(TagCategory).order_by(TagCategory.id).all()
    return categories


@router.get("/{category_id}", response_model=TagCategoryDetail)
def get_tag_category(category_id: int, db: Session = Depends(get_db)):
    """
    태그 카테고리 상세 조회 (태그 목록 포함)

    Args:
        category_id: 카테고리 ID

    Returns:
        TagCategoryDetail: 카테고리 상세 정보 (태그 포함)

    Raises:
        404: 카테고리를 찾을 수 없음
    """
    category = db.query(TagCategory).filter(TagCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"태그 카테고리 ID {category_id}를 찾을 수 없습니다",
        )
    return category


@router.post(
    "", response_model=TagCategoryResponse, status_code=status.HTTP_201_CREATED
)
def create_tag_category(
    category_data: TagCategoryCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    태그 카테고리 생성 (관리자)

    Args:
        category_data: 카테고리 생성 데이터

    Returns:
        TagCategoryResponse: 생성된 카테고리 정보

    Raises:
        400: 중복된 카테고리명
    """
    # 중복 체크
    existing = (
        db.query(TagCategory).filter(TagCategory.name == category_data.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{category_data.name}' 이름의 태그 카테고리가 이미 존재합니다",
        )

    # 생성
    new_category = TagCategory(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=TagCategoryResponse)
def update_tag_category(
    category_id: int,
    category_data: TagCategoryUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
):
    """
    태그 카테고리 수정 (관리자)

    Args:
        category_id: 카테고리 ID
        category_data: 수정 데이터

    Returns:
        TagCategoryResponse: 수정된 카테고리 정보

    Raises:
        404: 카테고리를 찾을 수 없음
        400: 중복된 카테고리명
    """
    category = db.query(TagCategory).filter(TagCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"태그 카테고리 ID {category_id}를 찾을 수 없습니다",
        )

    # 이름 중복 체크
    if category_data.name:
        existing = (
            db.query(TagCategory)
            .filter(
                TagCategory.name == category_data.name, TagCategory.id != category_id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{category_data.name}' 이름의 태그 카테고리가 이미 존재합니다",
            )

    # 수정
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_category(
    category_id: int, db: Session = Depends(get_db), _: bool = Depends(verify_api_key)
):
    """
    태그 카테고리 삭제 (관리자)

    Args:
        category_id: 카테고리 ID

    Raises:
        404: 카테고리를 찾을 수 없음
    """
    category = db.query(TagCategory).filter(TagCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"태그 카테고리 ID {category_id}를 찾을 수 없습니다",
        )

    db.delete(category)
    db.commit()
    return None
