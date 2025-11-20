# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class PacienteSimples(BaseModel):
    id: int
    nome: str
    telefone: str
    email: str
    cidade: str
    servico: str
    ativo: bool 

        
    class Config:
        from_attributes = True

class ConsultaSimples(BaseModel):
    id: int
    paciente_id: int
    paciente_nome: str
    data_hora: str

class DashboardStats(BaseModel):
    total_pacientes: int
    ativos: int
    inativos: int
    consultas_hoje: int
    proximos_agendamentos: List[ConsultaSimples]
    novos_pacientes: List[PacienteSimples]
