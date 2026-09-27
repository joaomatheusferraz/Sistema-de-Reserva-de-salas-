from enum import Enum


class Perfil(str, Enum):
    ALUNO = "aluno"
    PROFESSOR = "professor"
    COORDENADOR = "coordenador"
    EXTERNO = "externo"


class TipoEspaco(str, Enum):
    SALA = "sala"
    LABORATORIO = "laboratorio"
