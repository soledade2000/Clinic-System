# app/routes/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.dashboard import DashboardStats, PacienteSimples, ConsultaSimples
from app.crud.dashboard import get_dashboard_stats
from app.database import get_db

router = APIRouter()

@router.get("", response_model=DashboardStats)  # <-- apenas ""
def read_dashboard(db: Session = Depends(get_db)):
    stats = get_dashboard_stats(db)

    # Mapear pacientes e consultas para os schemas
    proximos_agendamentos = [
        ConsultaSimples(
            id=c.id,
            paciente_id=c.paciente_id,
            paciente_nome=c.paciente.nome_completo,
            data_hora=c.data_hora.isoformat()
        ) for c in stats["proximos_agendamentos"]
    ]

    novos_pacientes = [
    PacienteSimples(
        id=p.id,
        nome=p.nome_completo,
        telefone=p.telefone,
        email=p.email,
        cidade=p.endereco,  # ou extrair só cidade do endereço
        servico=p.servicos[0] if p.servicos else "-",  # pega primeiro serviço
        ativo=p.ativo
    )
    for p in stats["novos_pacientes"]
]

    return DashboardStats(
        total_pacientes=stats["total_pacientes"],
        ativos=stats["ativos"],
        inativos=stats["inativos"],
        consultas_hoje=stats["consultas_hoje"],
        proximos_agendamentos=proximos_agendamentos,
        novos_pacientes=novos_pacientes
    )
