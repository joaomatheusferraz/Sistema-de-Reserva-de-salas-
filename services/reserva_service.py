from datetime import datetime

from domain.enums import Perfil
from models.espaco_model import EspacoModel
from models.reserva_model import ReservaModel
from models.usuario_model import UsuarioModel
from services.historico_service import HistoricoService
from services.notificacao_service import NotificacaoService
from utils.validators import texto_obrigatorio


class ReservaService:

    STATUS_PENDENTE = "pendente"
    STATUS_RESERVADA = "reservada"

    def __init__(
        self,
        model=None,
        usuario_model=None,
        espaco_model=None,
        historico_service=None,
        notificacao_service=None,
    ):
        self.model = model or ReservaModel()
        self.usuario_model = usuario_model or UsuarioModel()
        self.espaco_model = espaco_model or EspacoModel()
        self.historico = historico_service or HistoricoService()
        self.notificacoes = notificacao_service or NotificacaoService()

    def criar(self, espaco_id, responsavel_id, inicio, fim, finalidade, perfil):
        self._validar_dados(
            espaco_id,
            responsavel_id,
            inicio,
            fim,
            finalidade,
            perfil,
        )

        usuario = self.usuario_model.buscar(responsavel_id)
        espaco = self.espaco_model.buscar(espaco_id)

        if not usuario or not usuario.get("ativo", True):
            raise ValueError("Usuário responsável não encontrado ou inativo.")
        if not espaco or not espaco.get("ativo", True):
            raise ValueError("Espaço não encontrado ou inativo.")

        if usuario.get("perfil") != perfil:
            raise ValueError("O perfil informado não corresponde ao usuário.")

        if perfil not in {Perfil.PROFESSOR.value, Perfil.EXTERNO.value}:
            raise PermissionError("Somente professor ou usuário externo pode solicitar reserva.")
        if perfil == Perfil.EXTERNO.value:
            autorizados = usuario.get("espacos_autorizados_ids", [])
            if autorizados and espaco_id not in autorizados:
                raise PermissionError("Usuário externo não tem acesso a esse espaço.")

        dados = {
            "espaco_id": espaco_id,
            "responsavel_id": responsavel_id,
            "inicio": inicio,
            "fim": fim,
            "finalidade": finalidade.strip(),
            "status": self.STATUS_PENDENTE,
            "aprovacao_necessaria": True,
            "analisada_por_id": None,
            "motivo_rejeicao": None,
        }
        reserva_id = self.model.criar_se_disponivel(dados)
        self._registrar(
            reserva_id,
            "criacao",
            responsavel_id,
            dados_novos=dados,
        )
        self._notificar(
            responsavel_id,
            "reserva_criada",
            "Sua solicitação de reserva foi criada.",
            reserva_id,
        )
        return reserva_id

    def listar_do_responsavel(self, responsavel_id):
        if not texto_obrigatorio(responsavel_id):
            raise ValueError("Informe o responsável da reserva.")
        return self.model.listar_por_responsavel(responsavel_id)

    def listar_pendentes(self, perfil):
        self._exigir_coordenador(perfil)
        return self.model.listar_por_status(self.STATUS_PENDENTE)

    def listar_calendario(self):
        return self.model.listar_ativas()

    def buscar(self, reserva_id):
        if not texto_obrigatorio(reserva_id):
            raise ValueError("Informe a reserva.")
        return self.model.buscar(reserva_id)

    def aprovar(self, reserva_id, coordenador_id, perfil):
        self._exigir_coordenador(perfil)
        reserva = self._obter_reserva(reserva_id)
        if reserva.get("status") != self.STATUS_PENDENTE:
            raise ValueError("Somente reservas pendentes podem ser aprovadas.")
        self.model.aprovar_se_disponivel(reserva_id, coordenador_id)
        self._registrar(reserva_id, "aprovacao", coordenador_id)
        self._notificar(
            reserva.get("responsavel_id"),
            "reserva_aprovada",
            "Sua solicitação de reserva foi aprovada.",
            reserva_id,
        )

    def rejeitar(self, reserva_id, coordenador_id, perfil, motivo=None):
        self._exigir_coordenador(perfil)
        if not texto_obrigatorio(motivo):
            raise ValueError("Informe o motivo da rejeição.")
        reserva = self._obter_reserva(reserva_id)
        if reserva.get("status") != self.STATUS_PENDENTE:
            raise ValueError("Somente reservas pendentes podem ser rejeitadas.")
        self.model.atualizar_status(reserva_id, {
            "status": "rejeitada",
            "aprovacao_necessaria": False,
            "analisada_por_id": coordenador_id,
            "motivo_rejeicao": motivo.strip(),
        })
        self._registrar(reserva_id, "rejeicao", coordenador_id)
        self._notificar(
            reserva.get("responsavel_id"),
            "reserva_rejeitada",
            "Sua solicitação de reserva foi rejeitada.",
            reserva_id,
        )

    def cancelar(self, reserva_id, responsavel_id, perfil):
        reserva = self._obter_reserva(reserva_id)
        self._exigir_dono_ou_coordenador(
            reserva,
            responsavel_id,
            perfil,
        )
        if reserva.get("status") in {"rejeitada", "cancelada"}:
            raise ValueError("Essa reserva já não está ativa.")
        self.model.atualizar_status(reserva_id, {
            "status": "cancelada",
        })
        self._registrar(reserva_id, "cancelamento", responsavel_id)
        self._notificar(
            reserva.get("responsavel_id"),
            "reserva_cancelada",
            "Sua reserva foi cancelada.",
            reserva_id,
        )

    def editar(self, reserva_id, responsavel_id, perfil, dados):
        reserva = self._obter_reserva(reserva_id)
        self._exigir_dono_ou_coordenador(
            reserva,
            responsavel_id,
            perfil,
        )
        if reserva.get("status") in {"rejeitada", "cancelada"}:
            raise ValueError("Essa reserva não pode ser editada.")
        self._validar_dados(
            dados.get("espaco_id"),
            reserva.get("responsavel_id"),
            dados.get("inicio"),
            dados.get("fim"),
            dados.get("finalidade"),
            reserva.get("perfil", perfil),
        )
        self.model.atualizar_se_disponivel(reserva_id, {
            "espaco_id": dados["espaco_id"],
            "inicio": dados["inicio"],
            "fim": dados["fim"],
            "finalidade": dados["finalidade"].strip(),
        })
        self._registrar(reserva_id, "alteracao", responsavel_id, dados_novos=dados)
        self._notificar(
            reserva.get("responsavel_id"),
            "reserva_alterada",
            "Sua reserva foi alterada.",
            reserva_id,
        )

    def _registrar(self, reserva_id, acao, executado_por_id, dados_novos=None):
        self.historico.registrar(
            "reserva",
            reserva_id,
            acao,
            executado_por_id,
            dados_novos=dados_novos,
        )

    def _notificar(self, usuario_id, tipo, mensagem, reserva_id):
        self.notificacoes.criar(usuario_id, tipo, mensagem, reserva_id)

    def _obter_reserva(self, reserva_id):
        reserva = self.buscar(reserva_id)
        if not reserva:
            raise ValueError("Reserva não encontrada.")
        return reserva

    @staticmethod
    def _exigir_coordenador(perfil):
        if perfil != Perfil.COORDENADOR.value:
            raise PermissionError("Somente coordenador pode analisar reservas.")

    @staticmethod
    def _exigir_dono_ou_coordenador(reserva, responsavel_id, perfil):
        eh_coordenador = perfil == Perfil.COORDENADOR.value
        eh_dono = reserva.get("responsavel_id") == responsavel_id
        if not eh_coordenador and not eh_dono:
            raise PermissionError("Usuário sem permissão para alterar a reserva.")

    def _validar_dados(
        self,
        espaco_id,
        responsavel_id,
        inicio,
        fim,
        finalidade,
        perfil,
    ):
        if not texto_obrigatorio(espaco_id):
            raise ValueError("Informe o espaço da reserva.")
        if not texto_obrigatorio(responsavel_id):
            raise ValueError("Informe o responsável da reserva.")
        if not isinstance(inicio, datetime) or not isinstance(fim, datetime):
            raise ValueError("Início e fim devem ser valores datetime.")
        if fim <= inicio:
            raise ValueError("O fim deve ser posterior ao início.")
        if not texto_obrigatorio(finalidade):
            raise ValueError("Informe a finalidade da reserva.")
        if perfil not in {
            Perfil.ALUNO.value,
            Perfil.PROFESSOR.value,
            Perfil.COORDENADOR.value,
            Perfil.EXTERNO.value,
        }:
            raise ValueError("Perfil inválido.")
        if perfil in {Perfil.PROFESSOR.value, Perfil.EXTERNO.value} \
                and not texto_obrigatorio(finalidade):
            raise ValueError("Informe a finalidade da reserva.")
