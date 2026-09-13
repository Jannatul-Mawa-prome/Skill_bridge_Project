from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.announcement import Announcement
from app.models.challenge import Challenge, UserChallenge
from app.models.discussion import Discussion
from app.models.event import Event, EventRegistration
from app.models.resource import Resource
from app.models.community import CommunityMembership
from app.models.profile import Profile


class CommunityContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_challenges(self, community_id: int) -> list[Challenge]:
        return self.db.execute(
            select(Challenge)
            .where(Challenge.community_id == community_id)
            .where(Challenge.is_active.is_(True))
            .order_by(Challenge.created_at.desc())
        ).scalars().all()

    def get_user_challenge_status(
        self,
        user_id: int,
        challenge_ids: list[int],
    ) -> dict[int, str]:
        if not challenge_ids:
            return {}
        rows = self.db.execute(
            select(UserChallenge.challenge_id, UserChallenge.status)
            .where(UserChallenge.user_id == user_id)
            .where(UserChallenge.challenge_id.in_(challenge_ids))
        ).all()
        return {challenge_id: status for challenge_id, status in rows}

    def complete_challenge(self, user_id: int, challenge_id: int) -> UserChallenge:
        progress = self.db.execute(
            select(UserChallenge)
            .where(UserChallenge.user_id == user_id)
            .where(UserChallenge.challenge_id == challenge_id)
        ).scalar_one_or_none()
        if progress:
            progress.status = "completed"
        else:
            progress = UserChallenge(
                user_id=user_id,
                challenge_id=challenge_id,
                status="completed",
            )
            self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_resources(self, community_id: int) -> list[Resource]:
        return self.db.execute(
            select(Resource)
            .where(Resource.community_id == community_id)
            .order_by(Resource.created_at.desc())
        ).scalars().all()

    def get_members(self, community_id: int, limit: int = 12):
        return self.db.execute(
            select(CommunityMembership, Profile)
            .join(Profile, Profile.user_id == CommunityMembership.user_id)
            .where(CommunityMembership.community_id == community_id)
            .order_by(CommunityMembership.joined_at.desc())
            .limit(limit)
        ).all()

    def get_discussions(self, community_id: int) -> list[Discussion]:
        return self.db.execute(
            select(Discussion)
            .where(Discussion.community_id == community_id)
            .order_by(Discussion.created_at.desc())
        ).scalars().all()

    def create_discussion(self, community_id: int, author_id: int, title: str, content: str | None = None) -> Discussion:
        discussion = Discussion(
            community_id=community_id,
            author_id=author_id,
            title=title,
            content=content,
            reply_count=0,
        )
        self.db.add(discussion)
        self.db.commit()
        self.db.refresh(discussion)
        return discussion

    def get_announcements(self, community_id: int) -> list[Announcement]:
        return self.db.execute(
            select(Announcement)
            .where(Announcement.community_id == community_id)
            .order_by(Announcement.created_at.desc())
        ).scalars().all()

    def get_events(self, community_id: int) -> list[Event]:
        return self.db.execute(
            select(Event)
            .where(Event.community_id == community_id)
            .order_by(Event.event_date)
        ).scalars().all()

    def get_registered_event_ids(
        self,
        user_id: int,
        event_ids: list[int],
    ) -> set[int]:
        if not event_ids:
            return set()
        rows = self.db.execute(
            select(EventRegistration.event_id)
            .where(EventRegistration.user_id == user_id)
            .where(EventRegistration.event_id.in_(event_ids))
        ).scalars().all()
        return set(rows)

    def register_for_event(self, user_id: int, event_id: int) -> EventRegistration:
        registration = self.db.execute(
            select(EventRegistration)
            .where(EventRegistration.user_id == user_id)
            .where(EventRegistration.event_id == event_id)
        ).scalar_one_or_none()
        if registration:
            return registration
        registration = EventRegistration(user_id=user_id, event_id=event_id)
        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)
        return registration
