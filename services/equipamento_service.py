from models.equipamento_model import EquipamentoModel
from utils.validators import texto_obrigatorio


class EquipamentoService:

    def __init__(self, model=None):
        self.model = model or EquipamentoModel()

    def criar(self, nome, descricao="", exige_autorizacao=False):
        if not texto_obrigatorio(nome):
            raise ValueError("Informe o nome do equipamento.")

        return self.model.criar({
            "nome": nome.strip(),
            "descricao": (descricao or "").strip(),
            "exige_autorizacao": bool(exige_autorizacao),
        })

    def buscar(self, equipamento_id):
        if not texto_obrigatorio(equipamento_id):
            raise ValueError("ID do equipamento inválido.")
        return self.model.buscar(equipamento_id)

    def listar(self, apenas_ativos=True):
        return self.model.listar(apenas_ativos=apenas_ativos)

    def atualizar(self, equipamento_id, dados):
        if not texto_obrigatorio(equipamento_id):
            raise ValueError("ID do equipamento inválido.")
        if not dados or not isinstance(dados, dict):
            raise ValueError("Dados de atualização inválidos.")
        if not texto_obrigatorio(dados.get("nome")):
            raise ValueError("Informe o nome do equipamento.")
        self.model.atualizar(equipamento_id, dados)

    def excluir(self, equipamento_id):
        if not texto_obrigatorio(equipamento_id):
            raise ValueError("ID do equipamento inválido.")
        self.model.excluir(equipamento_id)
