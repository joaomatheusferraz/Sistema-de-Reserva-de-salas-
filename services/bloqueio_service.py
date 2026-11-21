from datetime import datetime

from domain.enums import Perfil
from models.bloqueio_model import BloqueioModel
from models.espaco_model import EspacoModel
from services.historico_service import HistoricoService
from utils.validators import texto_obrigatorio


class BloqueioService:

    def __init__(self, model=None, espaco_model=None, historico_service=None, reserva_model=None):
        self.model = model or BloqueioModel()
        self.espaco_model = espaco_model or EspacoModel()
        self.historico = historico_service or HistoricoService()
        self.reserva_model = reserva_model

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

        conflitos = self.verificar_reservas_conflitantes(espaco_id, inicio, fim)

        bloqueio_id = self.model.criar({
            "espaco_id": espaco_id,
            "inicio": inicio,
            "fim": fim,
            "motivo": motivo.strip(),
            "responsavel_id": responsavel_id,
            "reservas_conflitantes_ids": [c.get("id") for c in conflitos if c.get("id")],
        })
        self.historico.registrar(
            "bloqueio",
            bloqueio_id,
            "criacao",
            responsavel_id,
            dados_novos={"motivo": motivo.strip(), "total_conflitos": len(conflitos)},
        )
        return bloqueio_id

    def verificar_reservas_conflitantes(self, espaco_id, inicio, fim):
        """Identifica reservas pendentes ou confirmadas que conflitam com o período (RN18)."""
        if not self.reserva_model:
            return []
        from models.reserva_model import ReservaModel
        ativas = self.reserva_model.listar_ativas()
        conflitos = []
        for r in ativas:
            if r.get("espaco_id") == espaco_id and ReservaModel._sobrepoe(
                inicio, fim, r.get("inicio"), r.get("fim")
            ):
                conflitos.append(r)
        return conflitos

    def listar(self, perfil, apenas_ativos=True):
        self._exigir_coordenador(perfil)
        return self.model.listar(apenas_ativos=apenas_ativos)

    def listar_vigentes(self):
        """Bloqueios ativos, para todos os perfis verem na agenda (seção 8)."""
        return self.model.listar(apenas_ativos=True)

    def remover(self, bloqueio_id, perfil, executado_por_id):
        self._exigir_coordenador(perfil)
        if not texto_obrigatorio(bloqueio_id):
            raise ValueError("Informe o bloqueio.")
        if not texto_obrigatorio(executado_por_id):
            raise ValueError("Informe o responsável pela remoção.")
        self.model.remover(bloqueio_id)
        self.historico.registrar(
            "bloqueio",
            bloqueio_id,
            "remocao",
            executado_por_id,
        )

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
