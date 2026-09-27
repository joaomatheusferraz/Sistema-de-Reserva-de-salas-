from services.bloqueio_service import BloqueioService


class BloqueioController:

    def __init__(self, service=None):
        self.service = service or BloqueioService()

    def criar_bloqueio(self, **dados):
        try:
            return True, self.service.criar(**dados)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def listar_bloqueios(self, perfil, apenas_ativos=True):
        try:
            return self.service.listar(perfil, apenas_ativos)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def remover_bloqueio(self, bloqueio_id, perfil, executado_por_id):
        try:
            self.service.remover(bloqueio_id, perfil, executado_por_id)
            return True, "Bloqueio removido com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)
