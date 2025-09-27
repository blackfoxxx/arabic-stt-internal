"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

# Import individual routers
from app.api.v1.auth import router as auth_router
from app.api.v1.media import router as media_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.test import router as test_router
# Placeholder imports for future implementation
# from app.api.v1.transcripts import router as transcripts_router
# from app.api.v1.exports import router as exports_router
# from app.api.v1.usage import router as usage_router
# from app.api.v1.webhooks import router as webhooks_router
# from app.api.v1.admin import router as admin_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers with their prefixes and tags
api_router.include_router(
    auth_router, 
    prefix="/auth", 
    tags=["authentication"]
)

api_router.include_router(
    media_router,
    prefix="/media",
    tags=["media"]
)

api_router.include_router(
    jobs_router,
    prefix="/jobs", 
    tags=["jobs"]
)

api_router.include_router(
    test_router,
    prefix="/test",
    tags=["testing"]
)

# TODO: Implement remaining routers
# api_router.include_router(
#     transcripts_router,
#     prefix="/transcripts",
#     tags=["transcripts"]
# )

# api_router.include_router(
#     exports_router,
#     prefix="/exports",
#     tags=["exports"]
# )

# api_router.include_router(
#     usage_router,
#     prefix="/usage", 
#     tags=["usage"]
# )

# api_router.include_router(
#     webhooks_router,
#     prefix="/webhooks",
#     tags=["webhooks"]
# )

# api_router.include_router(
#     admin_router,
#     prefix="/admin",
#     tags=["admin"]
# )