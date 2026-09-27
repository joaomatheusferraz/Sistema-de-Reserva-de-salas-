from firebase_admin import firestore

from utils.firebase_utils import init_firestore


class HistoricoModel:

    def __init__(self):
        self.collection = init_firestore().collection("historico")

    def criar(self, dados):
        documento = {
            **dados,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        return self.collection.add(documento)[1].id

    def listar_por_entidade(self, entidade, entidade_id):
        historico = []
        consulta = self.collection.where("entidade", "==", entidade).where(
            "entidade_id", "==", entidade_id
        )
        for documento in consulta.stream():
            dados = documento.to_dict()
            dados["id"] = documento.id
            historico.append(dados)
        return historico
