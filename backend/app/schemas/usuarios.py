#app/schemas/usuarios.py
from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, List
from .enums import CargoEnum


# ---------------- Base para usuários ----------------
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    cargo: CargoEnum
    ativo: bool = True

    model_config = {
        "from_attributes": True  # Pydantic V2
    }

# ---------------- Criação de usuário ----------------
class UsuarioCreate(UsuarioBase):
    senha: str
    confirma_senha: str

    @model_validator(mode="after")
    def check_senha_match(self):
        if self.senha != self.confirma_senha:
            raise ValueError("As senhas não coincidem")
        return self

# ---------------- Atualização de usuário ----------------
class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cargo: Optional[CargoEnum] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = None
    confirma_senha: Optional[str] = None

    @model_validator(mode="after")
    def check_senha_match(self):
        if self.senha and self.confirma_senha and self.senha != self.confirma_senha:
            raise ValueError("As senhas não coincidem")
        return self

    model_config = {
        "from_attributes": True
    }

# ---------------- Login ----------------
class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

# ---------------- Saída ----------------
class UsuarioOut(UsuarioBase):
    id: int

# ---------------- Listagem ----------------
class UsuarioList(UsuarioBase):
    total: int
    skip: int
    limit: int
    data: List[UsuarioOut]
