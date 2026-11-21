"""Controlador de bloqueios temporários de espaços pela coordenação."""

from services.bloqueio_service import BloqueioService


class BloqueioController:
    """Gerencia criação, consulta e cancelamento de bloqueios de salas."""

    def __init__(self, service=None):
        self.service = service or BloqueioService()

    def criar_bloqueio(self, **dados):
        """Cria um bloqueio temporário em um espaço físico."""
        try:
            return True, self.service.criar(**dados)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def listar_bloqueios(self, perfil, apenas_ativos=True):
        """Lista os bloqueios cadastrados no sistema."""
        try:
            return self.service.listar(perfil, apenas_ativos)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def listar_vigentes(self):
        """Lista apenas bloqueios ativos que ainda não expiraram."""
        return self.service.listar_vigentes()

    def remover_bloqueio(self, bloqueio_id, perfil, executado_por_id):
        """Remove/cancela um bloqueio temporário antes do fim de sua vigência."""
        try:
            self.service.remover(bloqueio_id, perfil, executado_por_id)
            return True, "Bloqueio removido com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)
