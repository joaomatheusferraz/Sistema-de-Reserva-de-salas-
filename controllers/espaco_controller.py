from services.espaco_service import EspacoService


class EspacoController:

    def __init__(self, service=None):
        self.service = service or EspacoService()

    def criar_espaco(self, **dados):
        try:
            return True, self.service.criar(**dados)
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def listar_espacos(self, apenas_ativos=True):
        return self.service.listar(apenas_ativos=apenas_ativos)

    def atualizar_espaco(self, espaco_id, dados):
        try:
            self.service.atualizar(espaco_id, dados)
            return True, "Espaço atualizado com sucesso!"
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def excluir_espaco(self, espaco_id):
        try:
            self.service.excluir(espaco_id)
            return True, "Espaço desativado com sucesso!"
        except Exception:
            return False, "Não foi possível desativar o espaço."
