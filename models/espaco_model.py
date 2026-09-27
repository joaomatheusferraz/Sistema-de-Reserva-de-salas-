from firebase_admin import firestore

from utils.firebase_utils import init_firestore


class EspacoModel:

    def __init__(self):
        self.db = init_firestore()
        self.collection = self.db.collection("espacos")

    def criar(self, dados):
        documento = {
            **dados,
            "ativo": dados.get("ativo", True),
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        return self.collection.add(documento)[1].id

    def listar(self, apenas_ativos=False):
        consulta = self.collection
        if apenas_ativos:
            consulta = consulta.where("ativo", "==", True)

        espacos = []
        for documento in consulta.stream():
            dados = documento.to_dict()
            dados["id"] = documento.id
            espacos.append(dados)
        return espacos

    def buscar(self, espaco_id):
        documento = self.collection.document(espaco_id).get()
        if not documento.exists:
            return None
        dados = documento.to_dict()
        dados["id"] = documento.id
        return dados

    def atualizar(self, espaco_id, dados):
        self.collection.document(espaco_id).update({
            **dados,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

    def excluir(self, espaco_id):
        self.collection.document(espaco_id).update({
            "ativo": False,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })
