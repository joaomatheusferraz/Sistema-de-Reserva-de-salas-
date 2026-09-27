from services.equipamento_service import EquipamentoService


class EquipamentoController:

    def __init__(self, service=None):
        self.service = service or EquipamentoService()

    def criar_equipamento(self, **dados):
        try:
            return True, self.service.criar(**dados)
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def listar_equipamentos(self, apenas_ativos=True):
        return self.service.listar(apenas_ativos=apenas_ativos)

    def atualizar_equipamento(self, equipamento_id, dados):
        try:
            self.service.atualizar(equipamento_id, dados)
            return True, "Equipamento atualizado com sucesso!"
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def excluir_equipamento(self, equipamento_id):
        try:
            self.service.excluir(equipamento_id)
            return True, "Equipamento desativado com sucesso!"
        except Exception:
            return False, "Não foi possível desativar o equipamento."
