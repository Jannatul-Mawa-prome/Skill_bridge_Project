from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.database.session import get_db
from app.models.community import Community
from app.models.roadmap import Module
from app.models.resource import Resource
from app.models.user import User
from app.schemas.community import ResourceCreateRequest, ResourceUpdateRequest, ResourceSchema

router = APIRouter(
    prefix="/api/v1/resources",
    tags=["Resources"]
)


@router.get("/", response_model=list[ResourceSchema])
def list_resources(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    resources = db.query(Resource).order_by(Resource.created_at.desc()).all()
    return resources


@router.post("/", response_model=ResourceSchema)
def create_resource(
    payload: ResourceCreateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    community = db.query(Community).filter(Community.id == payload.community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    if payload.module_id is not None:
        module = db.query(Module).filter(Module.id == payload.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        if module.roadmap.community_id != community.id:
            raise HTTPException(status_code=400, detail="Module does not belong to the selected community")

    resource = Resource(
        community_id=payload.community_id,
        module_id=payload.module_id,
        title=payload.title,
        resource_type=payload.resource_type,
        difficulty=payload.difficulty,
        url=payload.url,
        description=payload.description,
        is_active=True,
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/{resource_id}", response_model=ResourceSchema)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.put("/{resource_id}", response_model=ResourceSchema)
def update_resource(
    resource_id: int,
    payload: ResourceUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if payload.community_id is not None:
        community = db.query(Community).filter(Community.id == payload.community_id).first()
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        resource.community_id = payload.community_id

    if payload.module_id is not None:
        module = db.query(Module).filter(Module.id == payload.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        if module.roadmap.community_id != resource.community_id:
            raise HTTPException(status_code=400, detail="Module does not belong to the selected community")
        resource.module_id = payload.module_id

    if payload.title is not None:
        resource.title = payload.title
    if payload.resource_type is not None:
        resource.resource_type = payload.resource_type
    if payload.difficulty is not None:
        resource.difficulty = payload.difficulty
    if payload.url is not None:
        resource.url = payload.url
    if payload.description is not None:
        resource.description = payload.description
    if payload.is_active is not None:
        resource.is_active = payload.is_active

    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.is_active = False
    db.commit()
    return {"message": "Resource disabled successfully.", "resource_id": resource.id, "is_active": resource.is_active}
