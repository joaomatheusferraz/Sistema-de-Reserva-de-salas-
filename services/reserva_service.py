from datetime import datetime

from domain.enums import Perfil
from models.espaco_model import EspacoModel
from models.reserva_model import ReservaModel
from models.usuario_model import UsuarioModel
from utils.validators import texto_obrigatorio


class ReservaService:

    STATUS_PENDENTE = "pendente"
    STATUS_RESERVADA = "reservada"

    def __init__(self, model=None, usuario_model=None, espaco_model=None):
        self.model = model or ReservaModel()
        self.usuario_model = usuario_model or UsuarioModel()
        self.espaco_model = espaco_model or EspacoModel()

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

        if perfil == Perfil.ALUNO.value:
            raise PermissionError("Aluno não pode criar reservas.")

        aprovacao_necessaria = perfil != Perfil.COORDENADOR.value
        return self.model.criar({
            "espaco_id": espaco_id,
            "responsavel_id": responsavel_id,
            "inicio": inicio,
            "fim": fim,
            "finalidade": finalidade.strip(),
            "status": (
                self.STATUS_PENDENTE
                if aprovacao_necessaria
                else self.STATUS_RESERVADA
            ),
            "aprovacao_necessaria": aprovacao_necessaria,
            "analisada_por_id": None,
            "motivo_rejeicao": None,
        })

    def listar_do_responsavel(self, responsavel_id):
        if not texto_obrigatorio(responsavel_id):
            raise ValueError("Informe o responsável da reserva.")
        return self.model.listar_por_responsavel(responsavel_id)

    def buscar(self, reserva_id):
        if not texto_obrigatorio(reserva_id):
            raise ValueError("Informe a reserva.")
        return self.model.buscar(reserva_id)

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
