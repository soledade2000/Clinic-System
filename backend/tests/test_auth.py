import pytest
from app.schemas.enums import CargoEnum
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(
        transport=ASGITransport(app=app), # type: ignore
        base_url="http://test"
    ) as client:
        # ---------------- Registro ----------------
        register_data = {
            "nome": "Teste",
            "email": "teste@email.com",
            "senha": "123456",
            "confirma_senha": "123456",
            "cargo": CargoEnum.ADMIN.value,  # <- usa o .value do Enum
            "ativo": True
        }
        response = await client.post("/auth/register", json=register_data)
        print("Registro:", response.json())
        assert response.status_code in (200, 201), f"Falha no registro: {response.json()}"

        # ---------------- Login ----------------
        login_data = {
            "email": "teste@email.com",
            "senha": "123456"
        }
        response = await client.post("/auth/login", json=login_data)
        print("Login:", response.json())
        assert response.status_code == 200, f"Erro no login: {response.json()}"
        json_resp = response.json()
        assert "access_token" in json_resp
        assert json_resp["token_type"] == "bearer"

        # ---------------- Teste do token ----------------
        access_token = json_resp["access_token"]
        assert access_token is not None
