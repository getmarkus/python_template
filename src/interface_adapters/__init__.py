from fastapi import APIRouter

from .routers import issues

api_router = APIRouter()
api_router.include_router(issues.router, tags=["issues"])