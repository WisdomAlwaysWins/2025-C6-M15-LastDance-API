# app/api/v1/endpoints/admin.py
"""
관리자 API 엔드포인트
- Lambda가 생성한 임베딩 업데이트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db.session import get_db
from app.models import Artwork

# router = APIRouter()
