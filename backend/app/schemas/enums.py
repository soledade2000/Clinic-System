from enum import Enum

class EstadoCivilEnum(str, Enum):
    solteiro = "Solteiro(a)"
    casado = "Casado(a)"
    divorciado = "Divorciado(a)"
    viuvo = "Viúvo(a)"

class EscolaridadeEnum(str, Enum):
    fundamental = "Fundamental"
    medio = "Médio"
    superior = "Superior"
    pos_graduacao = "Pós-Graduação"
    mestrado = "Mestrado"
    doutorado = "Doutorado"

class ReligiaoEnum(str, Enum):
    catolico = "Católico"
    evangelico = "Evangelico"
    espirita = "Espirita"
    ateu = "Ateu"
    outra = "Outra"

class CargoEnum(str, Enum):
    ADMIN = "ADMIN"
    PSICOLOGO = "PSICOLOGO"
    SECRETARIA = "SECRETARIA"
    FISIOTERAPIA = "FISIOTERAPIA"
    MEDICO = "MEDICO"
    NUTRICIONISTA = "NUTRICIONISTA"
    CLINICO = "CLINICO"