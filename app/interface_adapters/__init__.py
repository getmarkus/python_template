from fastapi import APIRouter

from app.interface_adapters.endpoints import issues

api_router = APIRouter()
api_router.include_router(issues.router, tags=["issues"])