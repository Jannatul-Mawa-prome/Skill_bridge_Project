from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import Profile

class UserRepository:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.edu_email == email).first()

    @staticmethod
    def get_profile_by_roll(db: Session, roll: str) -> Profile | None:
        return db.query(Profile).filter(Profile.roll == roll).first()

    @staticmethod
    def create_user_with_profile(db: Session, user: User, profile: Profile):
        db.add(user)
        db.flush()  # To get user.id
        
        profile.user_id = user.id
        db.add(profile)
        db.commit()
        db.refresh(user)
        db.refresh(profile)
        return user, profile
