"""Controlador de gestão de espaços físicos (salas e laboratórios)."""

from services.espaco_service import EspacoService


class EspacoController:
    """Gerencia cadastro, consulta, edição e desativação de espaços físicos."""

    def __init__(self, service=None):
        self.service = service or EspacoService()

    def criar_espaco(self, **dados):
        """Cadastra uma nova sala ou laboratório no sistema."""
        try:
            return True, self.service.criar(**dados)
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def listar_espacos(self, apenas_ativos=True):
        """Lista os espaços físicos cadastrados."""
        return self.service.listar(apenas_ativos=apenas_ativos)

    def atualizar_espaco(self, espaco_id, dados):
        """Atualiza informações cadastrais de um espaço existente."""
        try:
            self.service.atualizar(espaco_id, dados)
            return True, "Espaço atualizado com sucesso!"
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def excluir_espaco(self, espaco_id):
        """Desativa um espaço físico para impedir novas reservas."""
        try:
            self.service.excluir(espaco_id)
            return True, "Espaço desativado com sucesso!"
        except Exception:
            return False, "Não foi possível desativar o espaço."
