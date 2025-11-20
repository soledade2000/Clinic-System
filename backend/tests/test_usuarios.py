# tests/test_usuarios.py
import pytest
from app.crud import usuarios as crud
from app.schemas import usuarios as usuario_schemas
from app.models.usuarios import CargoEnum

def test_criar_usuario(db_session):
    usuario_data = usuario_schemas.UsuarioCreate(
        nome="Teste User",
        email="testeuser@teste.com",
        senha="senha123",
        confirma_senha="senha123",
        cargo=CargoEnum.ADMIN  # Enum corrigido # type: ignore
    )
    usuario = crud.criar_usuario(db_session, usuario_data)
    assert usuario.nome == "Teste User"
    assert usuario.email == "testeuser@teste.com"
    assert usuario.cargo == CargoEnum.ADMIN

def test_atualizar_usuario(db_session):
    # cria usuário temporário
    usuario_data = usuario_schemas.UsuarioCreate(
        nome="Temp User",
        email="tempuser@teste.com",
        senha="senha123",
        confirma_senha="senha123",
        cargo=CargoEnum.ADMIN # type: ignore
    )
    usuario = crud.criar_usuario(db_session, usuario_data)

    # atualiza nome
    update_data = usuario_schemas.UsuarioUpdate(nome="Usuário Atualizado")
    usuario_atualizado = crud.atualizar_usuario(db_session, usuario.id, update_data)

    assert usuario_atualizado.nome == "Usuário Atualizado"
    assert usuario_atualizado.email == "tempuser@teste.com"
    assert usuario_atualizado.cargo == CargoEnum.ADMIN
