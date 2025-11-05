"""
LastDance API Pydantic Schemas

모든 API Request/Response 스키마 정의
"""

# 1️⃣ 의존성 없는 기본 스키마들
from app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate
from app.schemas.artist import ArtistCreate, ArtistResponse, ArtistUpdate
from app.schemas.visitor import VisitorCreate, VisitorResponse, VisitorUpdate

# 2️⃣ TagCategory (TagResponse보다 먼저)
from app.schemas.tag_category import (
    TagCategoryBase,
    TagCategoryCreate,
    TagCategoryDetail,
    TagCategoryResponse,
    TagCategoryUpdate,
)

# 3️⃣ Tag (TagCategoryBase 사용)
from app.schemas.tag import TagCreate, TagDetail, TagResponse, TagUpdate

# 4️⃣ Exhibition (ArtworkSummary, ExhibitionSummary 포함)
from app.schemas.exhibition import (
    ArtistSummary,
    ArtworkSummary,
    ExhibitionCreate,
    ExhibitionDetail,
    ExhibitionResponse,
    ExhibitionSummary,
    ExhibitionUpdate,
)

# 5️⃣ Artwork (ExhibitionSummary 사용)
from app.schemas.artwork import (
    ArtworkCreate,
    ArtworkDetail,
    ArtworkMatchRequest,
    ArtworkMatchResponse,
    ArtworkMatchResult,
    ArtworkResponse,
    ArtworkUpdate,
)

# 6️⃣ VisitHistory (VisitHistorySummary 포함)
from app.schemas.visit_history import (
    VisitHistoryCreate,
    VisitHistoryDetail,
    VisitHistoryResponse,
    VisitHistorySummary,
)

# 7️⃣ Reaction (ReactionSummary 포함)
from app.schemas.reaction import (
    ReactionCreate,
    ReactionDetail,
    ReactionResponse,
    ReactionSummary,
    ReactionUpdate,
)

# 8️⃣ Forward Reference 해결
TagCategoryResponse.model_rebuild()
TagCategoryDetail.model_rebuild()
TagResponse.model_rebuild()
TagDetail.model_rebuild()
ExhibitionDetail.model_rebuild()
ArtworkDetail.model_rebuild()
VisitHistoryDetail.model_rebuild()
ReactionDetail.model_rebuild()

__all__ = [
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
    # TagCategory
    "TagCategoryBase",
    "TagCategoryCreate",
    "TagCategoryUpdate",
    "TagCategoryResponse",
    "TagCategoryDetail",
    # Tag
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagDetail",
    # Exhibition
    "ExhibitionCreate",
    "ExhibitionUpdate",
    "ExhibitionResponse",
    "ExhibitionDetail",
    "ExhibitionSummary",
    "ArtworkSummary",
    "ArtistSummary",
    # Artwork
    "ArtworkCreate",
    "ArtworkUpdate",
    "ArtworkResponse",
    "ArtworkDetail",
    "ArtworkMatchRequest",
    "ArtworkMatchResult",
    "ArtworkMatchResponse",
    # VisitHistory
    "VisitHistoryCreate",
    "VisitHistoryResponse",
    "VisitHistoryDetail",
    "VisitHistorySummary",
    # Reaction
    "ReactionCreate",
    "ReactionUpdate",
    "ReactionResponse",
    "ReactionDetail",
    "ReactionSummary",
]