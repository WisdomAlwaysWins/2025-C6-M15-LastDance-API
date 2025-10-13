from fastapi import APIRouter
# from app.api.v1.endpoints import admin, reactions, exhibitions, artworks, visitor, visits, artists, venues

api_router = APIRouter()

# 라우터 등록
# api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
# api_router.include_router(visitor.router, prefix="/users", tags=["Users"])
# api_router.include_router(exhibitions.router, prefix="/exhibitions", tags=["Exhibitions"])
# api_router.include_router(artworks.router, prefix="/artworks", tags=["Artworks"])
# api_router.include_router(reactions.router, prefix="/reactions", tags=["Reactions"])
# api_router.include_router(visits.router, prefix="/visits", tags=["Visits"])
# api_router.include_router(venues.router, prefix="/venues", tags=["Venues"])
# api_router.include_router(artists.router, prefix="/artists", tags=["Artists"])