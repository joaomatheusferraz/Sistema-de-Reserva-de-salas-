from models.notificacao_model import NotificacaoModel


class NotificacaoService:

    def __init__(self, model=None):
        self.model = model or NotificacaoModel()

    def criar(self, usuario_id, tipo, mensagem, entidade_id=None):
        return self.model.criar({
            "usuario_id": usuario_id,
            "tipo": tipo,
            "mensagem": mensagem,
            "entidade_id": entidade_id,
        })

    def listar_do_usuario(self, usuario_id, apenas_nao_lidas=False):
        return self.model.listar_do_usuario(
            usuario_id,
            apenas_nao_lidas,
        )

    def marcar_como_lida(self, notificacao_id):
        self.model.marcar_como_lida(notificacao_id)
