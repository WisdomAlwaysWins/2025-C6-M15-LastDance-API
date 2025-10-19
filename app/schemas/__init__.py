"""
LastDance API Pydantic Schemas

모든 API Request/Response 스키마 정의
"""

from app.schemas.artist import ArtistCreate, ArtistResponse, ArtistUpdate
from app.schemas.artwork import (
    ArtworkCreate,
    ArtworkDetail,
    ArtworkResponse,
    ArtworkUpdate,
)
from app.schemas.exhibition import (
    ExhibitionCreate,
    ExhibitionDetail,
    ExhibitionResponse,
    ExhibitionUpdate,
)
from app.schemas.reaction import (
    ReactionCreate,
    ReactionDetail,
    ReactionResponse,
    ReactionUpdate,
)
from app.schemas.tag import TagCreate, TagDetail, TagResponse, TagUpdate
from app.schemas.tag_category import (
    TagCategoryCreate,
    TagCategoryDetail,
    TagCategoryResponse,
    TagCategoryUpdate,
)
from app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate
from app.schemas.visit_history import (
    VisitHistoryCreate,
    VisitHistoryDetail,
    VisitHistoryResponse,
)
from app.schemas.visitor import VisitorCreate, VisitorResponse, VisitorUpdate

# Forward Reference 해결 (순환 참조 방지)
TagCategoryDetail.model_rebuild()
TagDetail.model_rebuild()
ExhibitionDetail.model_rebuild()
ArtworkDetail.model_rebuild()
VisitHistoryDetail.model_rebuild()
ReactionDetail.model_rebuild()

__all__ = [
    # TagCategory
    "TagCategoryCreate",
    "TagCategoryUpdate",
    "TagCategoryResponse",
    "TagCategoryDetail",
    # Tag
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagDetail",
    # Venue
    "VenueCreate",
    "VenueUpdate",
    "VenueResponse",
    # Artist
    "ArtistCreate",
    "ArtistUpdate",
    "ArtistResponse",
    # Visitor
    "VisitorCreate",
    "VisitorUpdate",
    "VisitorResponse",
    # Exhibition
    "ExhibitionCreate",
    "ExhibitionUpdate",
    "ExhibitionResponse",
    "ExhibitionDetail",
    # Artwork
    "ArtworkCreate",
    "ArtworkUpdate",
    "ArtworkResponse",
    "ArtworkDetail",
    # VisitHistory
    "VisitHistoryCreate",
    "VisitHistoryResponse",
    "VisitHistoryDetail",
    # Reaction
    "ReactionCreate",
    "ReactionUpdate",
    "ReactionResponse",
    "ReactionDetail",
]
