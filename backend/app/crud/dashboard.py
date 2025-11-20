# app/crud/dashboard.py
from sqlalchemy.orm import Session
from app.models.pacientes import Paciente
from app.models.consultas import Consulta
from datetime import date, datetime, timedelta

def get_dashboard_stats(db: Session):
    total_pacientes = db.query(Paciente).count()
    ativos = db.query(Paciente).filter(Paciente.ativo == True).count()
    inativos = db.query(Paciente).filter(Paciente.ativo == False).count()

    hoje = date.today()
    consultas_hoje = db.query(Consulta).filter(Consulta.data_hora.between(
        datetime.combine(hoje, datetime.min.time()),
        datetime.combine(hoje, datetime.max.time())
    )).count()

    proximos_agendamentos = db.query(Consulta).filter(
        Consulta.data_hora >= datetime.now()
    ).order_by(Consulta.data_hora.asc()).limit(5).all()

    novos_pacientes = db.query(Paciente).order_by(Paciente.id.desc()).limit(5).all()

    return {
        "total_pacientes": total_pacientes,
        "ativos": ativos,
        "inativos": inativos,
        "consultas_hoje": consultas_hoje,
        "proximos_agendamentos": proximos_agendamentos,
        "novos_pacientes": novos_pacientes
    }
