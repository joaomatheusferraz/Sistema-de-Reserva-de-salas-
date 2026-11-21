from models.historico_model import HistoricoModel
from utils.validators import texto_obrigatorio


class HistoricoService:

    def __init__(self, model=None):
        self.model = model or HistoricoModel()

    def registrar(
        self,
        entidade,
        entidade_id,
        acao,
        executado_por_id,
        dados_anteriores=None,
        dados_novos=None,
    ):
        if not texto_obrigatorio(entidade):
            raise ValueError("Informe a entidade.")
        if not texto_obrigatorio(entidade_id):
            raise ValueError("Informe o ID da entidade.")
        if not texto_obrigatorio(acao):
            raise ValueError("Informe a ação executada.")

        return self.model.criar({
            "entidade": entidade,
            "entidade_id": entidade_id,
            "acao": acao,
            "executado_por_id": executado_por_id,
            "dados_anteriores": dados_anteriores or {},
            "dados_novos": dados_novos or {},
        })

    def listar_por_entidade(self, entidade, entidade_id):
        if not texto_obrigatorio(entidade) or not texto_obrigatorio(entidade_id):
            return []
        return self.model.listar_por_entidade(entidade, entidade_id)
