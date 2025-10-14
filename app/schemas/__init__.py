"""
LastDance API Pydantic Schemas

모든 API Request/Response 스키마 정의
"""

from app.schemas.tag_category import (
    TagCategoryCreate,
    TagCategoryUpdate,
    TagCategoryResponse,
    TagCategoryDetail
)
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagDetail
)
from app.schemas.venue import (
    VenueCreate,
    VenueUpdate,
    VenueResponse
)
from app.schemas.artist import (
    ArtistCreate,
    ArtistUpdate,
    ArtistResponse
)
from app.schemas.visitor import (
    VisitorCreate,
    VisitorUpdate,
    VisitorResponse
)
from app.schemas.exhibition import (
    ExhibitionCreate,
    ExhibitionUpdate,
    ExhibitionResponse,
    ExhibitionDetail
)
from app.schemas.artwork import (
    ArtworkCreate,
    ArtworkUpdate,
    ArtworkResponse,
    ArtworkDetail
)
from app.schemas.visit_history import (
    VisitHistoryCreate,
    VisitHistoryResponse,
    VisitHistoryDetail
)
from app.schemas.reaction import (
    ReactionCreate,
    ReactionUpdate,
    ReactionResponse,
    ReactionDetail
)

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