"""Aggregate v1 API router."""
from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    catalog,
    chat,
    instructor,
    keys,
    quiz,
    restrictions,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(restrictions.router, prefix="/restrictions", tags=["restrictions"])
api_router.include_router(instructor.router, prefix="/instructor", tags=["instructor"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(keys.router, prefix="/keys", tags=["keys"])
