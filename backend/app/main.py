from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.anonimizacao.router import router as anonimizacao_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.descoberta.router import router as descoberta_router
from app.modules.importacao.router import router as importacao_router
from app.modules.lgpd.router import router as lgpd_router
from app.modules.mascaramento.router import router as mascaramento_router
from app.modules.sinteticos.router import router as sinteticos_router

app = FastAPI(title="DataShield QA Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(importacao_router)
app.include_router(descoberta_router)
app.include_router(mascaramento_router)
app.include_router(anonimizacao_router)
app.include_router(sinteticos_router)
app.include_router(lgpd_router)
app.include_router(dashboard_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
