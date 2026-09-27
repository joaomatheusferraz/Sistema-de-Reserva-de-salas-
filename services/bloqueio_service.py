from datetime import datetime

from domain.enums import Perfil
from models.bloqueio_model import BloqueioModel
from models.espaco_model import EspacoModel
from utils.validators import texto_obrigatorio


class BloqueioService:

    def __init__(self, model=None, espaco_model=None):
        self.model = model or BloqueioModel()
        self.espaco_model = espaco_model or EspacoModel()

    def criar(
        self,
        espaco_id,
        inicio,
        fim,
        motivo,
        responsavel_id,
        perfil,
    ):
        self._exigir_coordenador(perfil)
        self._validar_dados(
            espaco_id,
            inicio,
            fim,
            motivo,
            responsavel_id,
        )
        espaco = self.espaco_model.buscar(espaco_id)
        if not espaco or not espaco.get("ativo", True):
            raise ValueError("Espaço não encontrado ou inativo.")

        return self.model.criar({
            "espaco_id": espaco_id,
            "inicio": inicio,
            "fim": fim,
            "motivo": motivo.strip(),
            "responsavel_id": responsavel_id,
        })

    def listar(self, perfil, apenas_ativos=True):
        self._exigir_coordenador(perfil)
        return self.model.listar(apenas_ativos=apenas_ativos)

    def remover(self, bloqueio_id, perfil):
        self._exigir_coordenador(perfil)
        if not texto_obrigatorio(bloqueio_id):
            raise ValueError("Informe o bloqueio.")
        self.model.remover(bloqueio_id)

    @staticmethod
    def _exigir_coordenador(perfil):
        if perfil != Perfil.COORDENADOR.value:
            raise PermissionError("Somente coordenador pode administrar bloqueios.")

    @staticmethod
    def _validar_dados(espaco_id, inicio, fim, motivo, responsavel_id):
        if not texto_obrigatorio(espaco_id):
            raise ValueError("Informe o espaço do bloqueio.")
        if not isinstance(inicio, datetime) or not isinstance(fim, datetime):
            raise ValueError("Início e fim devem ser valores datetime.")
        if fim <= inicio:
            raise ValueError("O fim deve ser posterior ao início.")
        if not texto_obrigatorio(motivo):
            raise ValueError("Informe o motivo do bloqueio.")
        if not texto_obrigatorio(responsavel_id):
            raise ValueError("Informe o responsável pelo bloqueio.")
