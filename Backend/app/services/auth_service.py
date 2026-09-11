from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.models.user import User
from app.models.profile import Profile
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:
    @staticmethod
    def register_user(db: Session, data: UserRegisterRequest):
        existing_user = UserRepository.get_user_by_email(db, data.edu_email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered."
            )

        existing_roll = UserRepository.get_profile_by_roll(db, data.roll)
        if existing_roll:
            raise HTTPException(
                status_code=400,
                detail="Roll number already registered."
            )

        hashed_password = hash_password(data.password)

        new_user = User(
            edu_email=data.edu_email,
            password_hash=hashed_password
        )
        
        new_profile = Profile(
            full_name=data.full_name,
            roll=data.roll,
            semester=data.semester,
            mobile=data.mobile
        )

        user, profile = UserRepository.create_user_with_profile(db, new_user, new_profile)
        
        return {
            "success": True,
            "message": "Registration successful.",
            "data": {
                "full_name": profile.full_name,
                "edu_email": user.edu_email,
                "roll": profile.roll
            }
        }
    @staticmethod
    def login_user(db: Session, user_data: UserLoginRequest):
        # Search by email or roll
        user = db.query(User).outerjoin(Profile).filter(
            (User.edu_email == user_data.login_id) | (Profile.roll == user_data.login_id)
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not verify_password(
            user_data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="User account is inactive"
            )
            
        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "edu_email": user.edu_email,
            "full_name": user.profile.full_name if user.profile else None,
            "is_admin": user.is_admin,
        }