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
            "descricao": descricao.strip(),
            "exige_autorizacao": bool(exige_autorizacao),
        })

    def listar(self, apenas_ativos=True):
        return self.model.listar(apenas_ativos=apenas_ativos)

    def atualizar(self, equipamento_id, dados):
        if not texto_obrigatorio(dados.get("nome")):
            raise ValueError("Informe o nome do equipamento.")
        self.model.atualizar(equipamento_id, dados)

    def excluir(self, equipamento_id):
        self.model.excluir(equipamento_id)
