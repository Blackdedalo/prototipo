from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import admin, ai, complaints, tracking


Base.metadata.create_all(bind=engine)

settings = get_settings()
app = FastAPI(title="Prototipo Denuncia Virtual PNP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router)
app.include_router(complaints.router)
app.include_router(admin.router)
app.include_router(tracking.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
