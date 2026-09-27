from models.historico_model import HistoricoModel


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
        return self.model.criar({
            "entidade": entidade,
            "entidade_id": entidade_id,
            "acao": acao,
            "executado_por_id": executado_por_id,
            "dados_anteriores": dados_anteriores or {},
            "dados_novos": dados_novos or {},
        })

    def listar_por_entidade(self, entidade, entidade_id):
        return self.model.listar_por_entidade(entidade, entidade_id)
