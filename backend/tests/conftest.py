# tests/conftest.py
import pytest
import pytest_asyncio
from datetime import date, datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.core.auth import router as auth_router
from app.main import app
from app.database import SessionLocal
from app import models
from app.schemas.enums import CargoEnum, EscolaridadeEnum, ReligiaoEnum, EstadoCivilEnum


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.include_router(auth_router)

# ---------------- Fixture DB ----------------
@pytest.fixture(scope="function")
def db_session():
    db: Session = SessionLocal()
    try:
        # Limpa tabelas essenciais pra evitar sujeira entre testes
        db.query(models.Consulta).delete()
        db.query(models.Paciente).delete()
        db.query(models.Usuario).delete()
        db.commit()
        yield db
    finally:
        db.close()


# ---------------- Event Loop ----------------
@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


# ---------------- Fixture Async Client ----------------
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), # type: ignore
        base_url="http://test"
    ) as ac:
        yield ac


# ---------------- Fixtures de Apoio ----------------
@pytest.fixture
def usuario_fixture(db_session):
    u = models.Usuario(
        nome="Usu Teste",
        email="u@test.com",
        senha_hash=pwd_context.hash("123456"),
        cargo=CargoEnum.ADMIN.value,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def paciente_fixture(db_session):
    data_nascimento = date(2000, 1, 1)
    idade = datetime.now().year - data_nascimento.year

    paciente = models.Paciente(
        nome_completo="Paciente Teste",
        nome_social=None,
        data_nascimento=data_nascimento,
        idade=idade,   
        cpf="12345678900",
        dependente=False,
        nome_responsavel=None,
        data_nascimento_responsavel=None,
        endereco="Rua Teste, 123",
        email="paciente@teste.com",
        telefone="999999999",
        escolaridade=EscolaridadeEnum.fundamental.value,
        religiao=ReligiaoEnum.ateu.value,
        estado_civil=EstadoCivilEnum.solteiro.value,
        servicos=["Psicologia"],
        disponibilidade_dias=["Segunda"],
        horario_atendimento="08:00-12:00",
        renda_familiar=1000.0
    )
    db_session.add(paciente)
    db_session.commit()
    db_session.refresh(paciente)
    return paciente
