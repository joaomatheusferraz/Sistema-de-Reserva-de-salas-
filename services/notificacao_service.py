from models.notificacao_model import NotificacaoModel
from utils.validators import texto_obrigatorio


class NotificacaoService:

    def __init__(self, model=None):
        self.model = model or NotificacaoModel()

    def criar(self, usuario_id, tipo, mensagem, entidade_id=None):
        if not texto_obrigatorio(usuario_id):
            raise ValueError("Informe o usuário da notificação.")
        if not texto_obrigatorio(tipo):
            raise ValueError("Informe o tipo da notificação.")
        if not texto_obrigatorio(mensagem):
            raise ValueError("Informe a mensagem da notificação.")

        return self.model.criar({
            "usuario_id": usuario_id,
            "tipo": tipo,
            "mensagem": mensagem,
            "entidade_id": entidade_id,
        })

    def listar_do_usuario(self, usuario_id, apenas_nao_lidas=False):
        if not texto_obrigatorio(usuario_id):
            return []
        return self.model.listar_do_usuario(
            usuario_id,
            apenas_nao_lidas,
        )

    def marcar_como_lida(self, notificacao_id):
        if not texto_obrigatorio(notificacao_id):
            raise ValueError("ID da notificação inválido.")
        self.model.marcar_como_lida(notificacao_id)
