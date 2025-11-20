# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.routes import usuarios, pacientes, consultas, ws_consultas, dashboard, pacientes_pdf
from app.core.auth import router as auth_router
from app.models import Usuario
from app.core.security import hash_password
from app.schemas.enums import CargoEnum

# ---------------- Criação das tabelas ----------------
Base.metadata.create_all(bind=engine)

# ---------------- Criar usuário master ----------------
def criar_usuario_master():
    db: Session = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == "master@admin.com").first()
        if not usuario:
            usuario_master = Usuario(
                nome="Master",
                email="master@admin.com",
                cargo=CargoEnum.ADMIN,
                ativo=True,
                senha_hash=hash_password("123456"),
            )
            db.add(usuario_master)
            db.commit()
            db.refresh(usuario_master)
            print("✅ Usuário master criado com sucesso!")
        else:
            print("ℹ️ Usuário master já existe, não será recriado")
    finally:
        db.close()


criar_usuario_master()

# ---------------- Instância do FastAPI ----------------
app = FastAPI(title="API Mente - Back-end")

# ---------------- CORS ----------------
origins = [
    "http://localhost:3000",  # Next.js
    "http://127.0.0.1:3000",
    "http://localhost:5500",  # HTML/JS puro
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Rotas ----------------
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
# NOTE: pacientes.router is included with prefix "/pacientes".
# Routes inside app/routes/pacientes.py should NOT repeat "/pacientes" in their decorators.
app.include_router(pacientes.router, prefix="/pacientes", tags=["Pacientes"])
# pacientes_pdf contains endpoints like GET /{paciente_id}/generate_pdf
# and is included under the same "/pacientes" prefix so final path is /pacientes/{id}/generate_pdf
app.include_router(pacientes_pdf.router, prefix="/pacientes", tags=["PDFs"])
app.include_router(consultas.router, prefix="/consultas", tags=["Consultas"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(ws_consultas.router, prefix="/ws", tags=["WebSocket Consultas"])

# ---------------- Root ----------------
@app.get("/")
async def root():
    return {"message": "API Mente está no ar!"}

# ---------------- OpenAPI Custom (Swagger + JWT) ----------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API Mente - Back-end",
        version="1.0.0",
        description="Documentação da API Mente",
        routes=app.routes,
    )

    # 🔑 JWT Bearer
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    # 🔒 Exige autenticação em todas rotas, exceto /auth/*
    for path, methods in openapi_schema["paths"].items():
        if not path.startswith("/auth"):
            for method in methods.values():
                method.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
