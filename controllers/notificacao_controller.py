from services.notificacao_service import NotificacaoService


class NotificacaoController:

    def __init__(self, service=None):
        self.service = service or NotificacaoService()

    def listar_do_usuario(self, usuario_id, apenas_nao_lidas=False):
        try:
            notificacoes = self.service.listar_do_usuario(usuario_id, apenas_nao_lidas)
        except Exception:
            return []
        return sorted(
            notificacoes,
            key=lambda item: str(item.get("created_at") or ""),
            reverse=True,
        )

    def marcar_como_lida(self, notificacao_id):
        try:
            self.service.marcar_como_lida(notificacao_id)
            return True
        except Exception:
            return False
