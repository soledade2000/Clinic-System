# app/schemas/pacientes.py
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator, ConfigDict
from typing import Optional, List
from datetime import date
from .enums import EscolaridadeEnum, ReligiaoEnum, EstadoCivilEnum


class PacienteBase(BaseModel):
    nome_completo: str
    nome_social: Optional[str] = None
    data_nascimento: date
    cpf: str
    dependente: bool = False
    nome_responsavel: Optional[str] = None
    data_nascimento_responsavel: Optional[date] = None
    endereco: str
    email: EmailStr
    telefone: str
    escolaridade: EscolaridadeEnum
    religiao: ReligiaoEnum
    estado_civil: EstadoCivilEnum
    servicos: List[str]
    disponibilidade_dias: List[str]
    horario_atendimento: str
    renda_familiar: Optional[float] = Field(..., description="Renda mensal em reais")
    ativo: Optional[bool] = True

    # 🔹 Novo campo: forma de pagamento
    forma_pagamento: Optional[str] = Field(default=None, description="Forma de pagamento do paciente")

    @field_validator("renda_familiar")
    def validar_renda(cls, v):
        if v is not None and v < 0:
            raise ValueError("A renda familiar não pode ser negativa")
        return v


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    nome_completo: Optional[str] = None
    nome_social: Optional[str] = None
    data_nascimento: Optional[date] = None
    endereco: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    escolaridade: Optional[EscolaridadeEnum] = None
    religiao: Optional[ReligiaoEnum] = None
    estado_civil: Optional[EstadoCivilEnum] = None
    servicos: Optional[List[str]] = None
    disponibilidade_dias: Optional[List[str]] = None
    horario_atendimento: Optional[str] = None
    renda_familiar: Optional[float] = None
    forma_pagamento: Optional[str] = None  # ✅ Novo campo
    ativo: Optional[bool] = None

    @field_validator("renda_familiar")
    def validar_renda(cls, value):
        if value is not None and value < 0:
            raise ValueError("A renda não pode ser negativa")
        return value


class PacienteOut(PacienteBase):
    id: int
    arquivos: Optional[List[dict]] = []  # ✅ Retorna lista de arquivos do paciente (uploads)
    ficha_pdf: Optional[str] = None

    @computed_field
    @property
    def idade(self) -> int:
        today = date.today()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )

    model_config = ConfigDict(from_attributes=True)
