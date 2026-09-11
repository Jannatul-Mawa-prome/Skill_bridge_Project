from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register(
    user: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    return AuthService.register_user(db, user)

@router.post("/login")
def login(
    user: UserLoginRequest,
    db: Session = Depends(get_db)
):
    return AuthService.login_user(db, user)
