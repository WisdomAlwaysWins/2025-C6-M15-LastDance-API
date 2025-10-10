"""
모든 스키마를 한 곳에서 임포트
"""
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.artist import ArtistCreate, ArtistUpdate, ArtistResponse
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse
from app.schemas.exhibition import (
    ExhibitionCreate, 
    ExhibitionUpdate, 
    ExhibitionResponse,
    ExhibitionDetailResponse
)
from app.schemas.artwork import (
    ArtworkCreate, 
    ArtworkUpdate, 
    ArtworkResponse,
    ArtworkDetailResponse
)
from app.schemas.reaction import (
    ReactionCreate, 
    ReactionUpdate, 
    ReactionResponse,
    ReactionDetailResponse,
    ReviewResponse  # 레거시 호환
)
from app.schemas.visit_history import VisitHistoryCreate, VisitHistoryResponse
from app.schemas.tag import TagCreate, TagResponse

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Artist
    "ArtistCreate",
    "ArtistUpdate",
    "ArtistResponse",
    # Venue
    "VenueCreate",
    "VenueUpdate",
    "VenueResponse",
    # Exhibition
    "ExhibitionCreate",
    "ExhibitionUpdate",
    "ExhibitionResponse",
    "ExhibitionDetailResponse",
    # Artwork
    "ArtworkCreate",
    "ArtworkUpdate",
    "ArtworkResponse",
    "ArtworkDetailResponse",
    # Reaction (Review 대체)
    "ReactionCreate",
    "ReactionUpdate",
    "ReactionResponse",
    "ReactionDetailResponse",
    "ReviewResponse",  # 레거시 호환
    # VisitHistory
    "VisitHistoryCreate",
    "VisitHistoryResponse",
    # Tag
    "TagCreate",
    "TagResponse",
]