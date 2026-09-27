from domain.enums import TipoEspaco
from models.espaco_model import EspacoModel
from utils.validators import texto_obrigatorio


class EspacoService:

    def __init__(self, model=None):
        self.model = model or EspacoModel()

    def criar(self, nome, tipo, capacidade, localizacao=None,
              caracteristicas=None, equipamentos_ids=None,
              regras_especificas=None):
        if not texto_obrigatorio(nome):
            raise ValueError("Informe o nome do espaço.")
        if tipo not in {item.value for item in TipoEspaco}:
            raise ValueError("Tipo de espaço inválido.")
        if not isinstance(capacidade, int) or capacidade <= 0:
            raise ValueError("A capacidade deve ser um inteiro positivo.")

        return self.model.criar({
            "nome": nome.strip(),
            "tipo": tipo,
            "capacidade": capacidade,
            "localizacao": localizacao or {},
            "caracteristicas": caracteristicas or [],
            "equipamentos_ids": equipamentos_ids or [],
            "regras_especificas": regras_especificas or [],
        })

    def listar(self, apenas_ativos=True):
        return self.model.listar(apenas_ativos=apenas_ativos)

    def atualizar(self, espaco_id, dados):
        if not texto_obrigatorio(dados.get("nome")):
            raise ValueError("Informe o nome do espaço.")
        if dados.get("tipo") not in {item.value for item in TipoEspaco}:
            raise ValueError("Tipo de espaço inválido.")
        if not isinstance(dados.get("capacidade"), int) or dados["capacidade"] <= 0:
            raise ValueError("A capacidade deve ser um inteiro positivo.")
        self.model.atualizar(espaco_id, dados)

    def excluir(self, espaco_id):
        self.model.excluir(espaco_id)
