from datetime import time
from enum import Enum


class Perfil(str, Enum):
    ALUNO = "aluno"
    PROFESSOR = "professor"
    COORDENADOR = "coordenador"
    EXTERNO = "externo"


class TipoEspaco(str, Enum):
    SALA = "sala"
    LABORATORIO = "laboratorio"


class StatusReserva(str, Enum):
    PENDENTE = "pendente"
    RESERVADA = "reservada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"
    BLOQUEADO = "bloqueado"


HORA_ABERTURA = time(7, 0)
HORA_FECHAMENTO = time(23, 0)

PODEM_RESERVAR = {Perfil.PROFESSOR.value, Perfil.EXTERNO.value, Perfil.COORDENADOR.value}
