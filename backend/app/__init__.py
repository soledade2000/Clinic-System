from fastapi import FastAPI
from app.routes import usuarios_router, pacientes_router, consultas_router
from app.models import Usuario, Paciente, Consulta # Isso é mais para referência ou para evitar conflitos de nome.
from app.core.auth import router as auth_router 
from app.core.auth import router as auth_router
from app.routes.usuarios import router as usuarios_router
from app.routes.pacientes import router as pacientes_router
from app.routes.consultas import router as consultas_router

# Cria a instância da sua aplicação FastAPI
app = FastAPI()

# Inclui os roteadores para que o FastAPI saiba dos endpoints
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(pacientes_router)
app.include_router(consultas_router)