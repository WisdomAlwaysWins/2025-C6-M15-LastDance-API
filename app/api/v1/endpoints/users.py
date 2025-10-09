from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    사용자 생성 (관람객 회원가입)
    UUID는 iOS 앱에서 생성해서 전달
    """
    # UUID 중복 확인
    existing_user = db.query(User).filter(User.uuid == user.uuid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this UUID already exists")
    
    # 이메일 중복 확인 (이메일이 있는 경우만)
    if user.email:
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    사용자 조회
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/uuid/{uuid}", response_model=UserResponse)
async def get_user_by_uuid(
    uuid: str,
    db: Session = Depends(get_db)
):
    """
    UUID로 사용자 조회 (iOS 앱에서 주로 사용)
    """
    user = db.query(User).filter(User.uuid == uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user