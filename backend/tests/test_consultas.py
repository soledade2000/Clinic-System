# tests/test_consultas.py
import pytest
from datetime import datetime, date, time
from app.crud import consultas as crud
from app.schemas.consultas import ConsultaCreate, ConsultaUpdate

def test_criar_consulta(db_session, paciente_fixture, usuario_fixture):
    data_hora_consulta = datetime.combine(date.today(), time(hour=8, minute=0))

    consulta_data = ConsultaCreate(
        paciente_id=paciente_fixture.id,
        usuario_id=usuario_fixture.id,
        data_hora=data_hora_consulta,
        status="agendada",
    )
    consulta = crud.criar_consulta(db_session, consulta_data)

    assert getattr(consulta, "id") is not None
    assert getattr(consulta, "paciente_id") == paciente_fixture.id
    assert getattr(consulta, "usuario_id") == usuario_fixture.id
    assert getattr(consulta, "data_hora") == data_hora_consulta
    assert getattr(consulta, "status") == "agendada"

def test_atualizar_consulta(db_session, paciente_fixture, usuario_fixture):
    data_hora_consulta = datetime.combine(date.today(), time(hour=9, minute=0))

    consulta_data = ConsultaCreate(
        paciente_id=paciente_fixture.id,
        usuario_id=usuario_fixture.id,
        data_hora=data_hora_consulta,
        status="agendada",
    )
    consulta = crud.criar_consulta(db_session, consulta_data)

    update_data = ConsultaUpdate(status="concluida")
    consulta_atualizada = crud.atualizar_consulta(
        db_session, int(getattr(consulta, "id")), update_data
    )

    assert int(getattr(consulta_atualizada, "id")) == int(getattr(consulta, "id"))
    assert getattr(consulta_atualizada, "status") == "concluida"
