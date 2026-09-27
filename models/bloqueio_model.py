from firebase_admin import firestore

from utils.firebase_utils import init_firestore


class BloqueioModel:

    def __init__(self):
        self.db = init_firestore()
        self.collection = self.db.collection("bloqueios")

    def criar(self, dados):
        documento = {
            **dados,
            "ativo": True,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        return self.collection.add(documento)[1].id

    def listar(self, apenas_ativos=True):
        consulta = self.collection
        if apenas_ativos:
            consulta = consulta.where("ativo", "==", True)

        bloqueios = []
        for documento in consulta.stream():
            dados = documento.to_dict()
            dados["id"] = documento.id
            bloqueios.append(dados)
        return bloqueios

    def remover(self, bloqueio_id):
        self.collection.document(bloqueio_id).update({
            "ativo": False,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })
