from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.community_content_repository import CommunityContentRepository
from app.repositories.community_repository import CommunityRepository


class CommunityContentService:
    def __init__(self, db: Session):
        self.community_repo = CommunityRepository(db)
        self.content_repo = CommunityContentRepository(db)

    def require_membership(self, user: User, community_id: int) -> None:
        if not self.community_repo.get_community_by_id(community_id):
            raise HTTPException(status_code=404, detail="Community not found")
        if not self.community_repo.get_membership(user.id, community_id):
            raise HTTPException(
                status_code=403,
                detail="Not a member of this community",
            )

    def get_challenges(self, user: User, community_id: int):
        self.require_membership(user, community_id)
        challenges = self.content_repo.get_challenges(community_id)
        statuses = self.content_repo.get_user_challenge_status(
            user.id,
            [challenge.id for challenge in challenges],
        )
        for challenge in challenges:
            challenge.user_status = statuses.get(challenge.id)
        return challenges

    def complete_challenge(self, user: User, community_id: int, challenge_id: int):
        self.require_membership(user, community_id)
        challenge = next(
            (
                challenge
                for challenge in self.content_repo.get_challenges(community_id)
                if challenge.id == challenge_id
            ),
            None,
        )
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        return self.content_repo.complete_challenge(user.id, challenge_id)

    def get_resources(self, user: User, community_id: int):
        self.require_membership(user, community_id)
        return self.content_repo.get_resources(community_id)

    def get_discussions(self, user: User, community_id: int):
        self.require_membership(user, community_id)
        return self.content_repo.get_discussions(community_id)

    def get_announcements(self, user: User, community_id: int):
        self.require_membership(user, community_id)
        return self.content_repo.get_announcements(community_id)

    def get_events(self, user: User, community_id: int):
        self.require_membership(user, community_id)
        events = self.content_repo.get_events(community_id)
        registered = self.content_repo.get_registered_event_ids(
            user.id,
            [event.id for event in events],
        )
        for event in events:
            event.is_registered = event.id in registered
        return events

    def register_for_event(self, user: User, community_id: int, event_id: int):
        self.require_membership(user, community_id)
        event = next(
            (
                event
                for event in self.content_repo.get_events(community_id)
                if event.id == event_id
            ),
            None,
        )
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return self.content_repo.register_for_event(user.id, event_id)
