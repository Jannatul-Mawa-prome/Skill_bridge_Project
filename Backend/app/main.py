from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.community import router as community_router
from app.api.v1.resources import router as resources_router

app = FastAPI(
    title="SkillBridge API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(community_router)
app.include_router(roadmap_router)
app.include_router(resources_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to SkillBridge API "
    }