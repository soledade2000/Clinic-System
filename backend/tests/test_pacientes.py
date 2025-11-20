#test_pacientes.py
import pytest
from datetime import date
from app.crud import paciente as crud
from app.schemas.enums import EscolaridadeEnum, ReligiaoEnum, EstadoCivilEnum
from app.schemas.pacientes import PacienteCreate, PacienteUpdate


def test_criar_paciente(db_session):
    paciente_data = PacienteCreate(
        nome_completo="Teste Paciente",
        nome_social=None,
        data_nascimento=date(2000, 1, 1),
        cpf="99999999999",
        dependente=False,
        nome_responsavel=None,
        data_nascimento_responsavel=None,
        endereco="Rua Teste, 123",
        email="teste@teste.com",
        telefone="999999999",
        escolaridade=EscolaridadeEnum.fundamental,
        religiao=ReligiaoEnum.ateu,
        estado_civil=EstadoCivilEnum.solteiro,
        servicos=["Psicologia"],
        disponibilidade_dias=["Segunda"],
        horario_atendimento="08:00-12:00",
        renda_familiar=1000.0
    )
    paciente = crud.criar_paciente(db_session, paciente_data)
    assert paciente.nome_completo == "Teste Paciente" # type: ignore

def test_atualizar_paciente(db_session):
    paciente_data = PacienteCreate(
        nome_completo="Temp Paciente",
        nome_social=None,
        data_nascimento=date(2000, 1, 1),
        cpf="88888888888",
        dependente=False,
        nome_responsavel=None,
        data_nascimento_responsavel=None,
        endereco="Rua Teste, 456",
        email="temppaciente@teste.com",
        telefone="999999998",
        escolaridade=EscolaridadeEnum.medio,
        religiao=ReligiaoEnum.ateu,
        estado_civil=EstadoCivilEnum.solteiro,
        servicos=["Psicologia"],
        disponibilidade_dias=["Terça"],
        horario_atendimento="08:00-12:00",
        renda_familiar=1200.0,
    )

    paciente = crud.criar_paciente(db_session, paciente_data)

    update_data = PacienteUpdate(nome_completo="Paciente Atualizado")
    paciente_atualizado = crud.atualizar_paciente(db_session, paciente.id, update_data) # type: ignore

    assert paciente_atualizado.nome_completo == "Paciente Atualizado" # type: ignore

