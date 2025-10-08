"""
모든 스키마를 한 곳에서 임포트
"""
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.exhibition import ExhibitionCreate, ExhibitionUpdate, ExhibitionResponse
from app.schemas.artwork import ArtworkCreate, ArtworkUpdate, ArtworkResponse
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewPrepareResponse
from app.schemas.visit_history import VisitHistoryCreate, VisitHistoryResponse

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "ExhibitionCreate",
    "ExhibitionUpdate",
    "ExhibitionResponse",
    "ArtworkCreate",
    "ArtworkUpdate",
    "ArtworkResponse",
    "TagCreate",
    "TagResponse",
    "ReviewCreate",
    "ReviewResponse",
    "ReviewPrepareResponse",
    "VisitHistoryCreate",
    "VisitHistoryResponse",
]