"""Controlador de notificações internas do sistema."""

from services.notificacao_service import NotificacaoService


class NotificacaoController:
    """Gerencia consulta e leitura de notificações dos usuários."""

    def __init__(self, service=None):
        self.service = service or NotificacaoService()

    def listar_do_usuario(self, usuario_id, apenas_nao_lidas=False):
        """Lista notificações de um usuário em ordem decrescente de criação."""
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
        """Marca uma notificação específica como lida."""
        try:
            self.service.marcar_como_lida(notificacao_id)
            return True
        except Exception:
            return False
