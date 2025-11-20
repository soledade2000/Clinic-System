# app/models/pacientes.py
from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    nome_social = Column(String)
    data_nascimento = Column(Date, nullable=False)
    idade = Column(Integer, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    dependente = Column(Boolean, default=False)
    nome_responsavel = Column(String)
    data_nascimento_responsavel = Column(Date)
    idade_responsavel = Column(Integer)
    endereco = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    escolaridade = Column(String, nullable=False)
    religiao = Column(String)
    estado_civil = Column(String)
    servicos = Column(ARRAY(String), nullable=False)
    disponibilidade_dias = Column(ARRAY(String), nullable=False)
    horario_atendimento = Column(String, nullable=False)
    renda_familiar = Column(Float)
    ativo = Column(Boolean, default=True)
    forma_pagamento = Column(String, nullable=True)
    ficha_pdf = Column(String, nullable=True)  # mantive aqui (opcional)

    consultas = relationship("Consulta", back_populates="paciente")
