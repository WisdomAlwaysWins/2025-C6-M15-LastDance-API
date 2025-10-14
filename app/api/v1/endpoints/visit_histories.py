# app/api/v1/endpoints/reactions.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.reaction import Reaction
from app.models.artwork import Artwork
from app.models.visitor import Visitor
from app.models.visit_history import VisitHistory
from app.models.tag import Tag
from app.schemas.reaction import (
    ReactionCreate,
    ReactionUpdate,
    ReactionResponse,
    ReactionDetail
)

router = APIRouter(prefix="/reactions", tags=["Reactions"])


@router.get("", response_model=List[ReactionResponse])
def get_reactions(
    artwork_id: Optional[int] = Query(None, description="작품 ID"),
    visitor_id: Optional[int] = Query(None, description="관람객 ID"),
    visit_id: Optional[int] = Query(None, description="방문 기록 ID"),
    db: Session = Depends(get_db)
):
    """
    반응 전체 조회
    
    Args:
        artwork_id: 작품 ID로 필터링
        visitor_id: 관람객 ID로 필터링
        visit_id: 방문 기록 ID로 필터링
        
    Returns:
        List[ReactionResponse]: 반응 목록
        
    Raises:
        404: 존재하지 않는 artwork_id, visitor_id, visit_id
    """
    # Artwork 존재 여부 확인
    if artwork_id:
        artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
        if not artwork:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artwork with id {artwork_id} not found"
            )
    
    # Visitor 존재 여부 확인
    if visitor_id:
        visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
        if not visitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Visitor with id {visitor_id} not found"
            )
    
    # VisitHistory 존재 여부 확인
    if visit_id:
        visit = db.query(VisitHistory).filter(VisitHistory.id == visit_id).first()
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"VisitHistory with id {visit_id} not found"
            )
    
    query = db.query(Reaction)
    
    if artwork_id:
        query = query.filter(Reaction.artwork_id == artwork_id)
    if visitor_id:
        query = query.filter(Reaction.visitor_id == visitor_id)
    if visit_id:
        query = query.filter(Reaction.visit_id == visit_id)
    
    reactions = query.order_by(Reaction.created_at.desc()).all()
    return reactions


@router.get("/{reaction_id}", response_model=ReactionDetail)
def get_reaction(
    reaction_id: int,
    db: Session = Depends(get_db)
):
    """
    반응 상세 조회 (작품, 관람객, 태그 포함)
    """
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reaction with id {reaction_id} not found"
        )
    return reaction


@router.post("", response_model=ReactionDetail, status_code=status.HTTP_201_CREATED)
def create_reaction(
    reaction_data: ReactionCreate,
    db: Session = Depends(get_db)
):
    """
    반응 생성
    
    Returns:
        ReactionDetail: 생성된 반응 정보 (작품, 관람객, 태그 포함)
        
    Raises:
        404: 존재하지 않는 artwork_id, visitor_id, visit_id, tag_ids
        400: comment와 tag_ids 둘 다 없음
    """
    # Artwork 존재 여부 확인
    artwork = db.query(Artwork).filter(Artwork.id == reaction_data.artwork_id).first()
    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork with id {reaction_data.artwork_id} not found"
        )
    
    # Visitor 존재 여부 확인
    visitor = db.query(Visitor).filter(Visitor.id == reaction_data.visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Visitor with id {reaction_data.visitor_id} not found"
        )
    
    # Visit 존재 여부 확인 (선택)
    if reaction_data.visit_id:
        visit = db.query(VisitHistory).filter(VisitHistory.id == reaction_data.visit_id).first()
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"VisitHistory with id {reaction_data.visit_id} not found"
            )
    
    # Reaction 생성
    reaction_dict = reaction_data.model_dump(exclude={'tag_ids'})
    new_reaction = Reaction(**reaction_dict)
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)
    
    # Tag 연결
    if reaction_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(reaction_data.tag_ids)).all()
        
        found_ids = {tag.id for tag in tags}
        missing_ids = set(reaction_data.tag_ids) - found_ids
        if missing_ids:
            db.delete(new_reaction)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tags with ids {sorted(missing_ids)} not found"
            )
        
        new_reaction.tags.extend(tags)
        db.commit()
        db.refresh(new_reaction)
    
    return new_reaction


@router.put("/{reaction_id}", response_model=ReactionDetail)
def update_reaction(
    reaction_id: int,
    reaction_data: ReactionUpdate,
    db: Session = Depends(get_db)
):
    """
    반응 수정
    
    Returns:
        ReactionDetail: 수정된 반응 정보 (작품, 관람객, 태그 포함)
        
    Raises:
        404: 반응을 찾을 수 없음 또는 존재하지 않는 tag_ids
        400: comment와 tag_ids 둘 다 비움
    """
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reaction with id {reaction_id} not found"
        )
    
    # comment 수정
    if reaction_data.comment is not None:
        reaction.comment = reaction_data.comment
    
    # tag_ids 수정
    if reaction_data.tag_ids is not None:
        reaction.tags.clear()
        
        if reaction_data.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(reaction_data.tag_ids)).all()
            
            found_ids = {tag.id for tag in tags}
            missing_ids = set(reaction_data.tag_ids) - found_ids
            if missing_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tags with ids {sorted(missing_ids)} not found"
                )
            
            reaction.tags.extend(tags)
    
    # Validation: comment와 tag_ids 둘 다 비어있으면 에러
    if not reaction.comment and not reaction.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either comment or tag_ids must be provided"
        )
    
    db.commit()
    db.refresh(reaction)
    return reaction


@router.delete("/{reaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reaction(
    reaction_id: int,
    db: Session = Depends(get_db)
):
    """
    반응 삭제
    """
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reaction with id {reaction_id} not found"
        )
    
    db.delete(reaction)
    db.commit()
    return None