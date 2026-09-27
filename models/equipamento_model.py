from firebase_admin import firestore

from utils.firebase_utils import init_firestore


class EquipamentoModel:

    def __init__(self):
        self.db = init_firestore()
        self.collection = self.db.collection("equipamentos")

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

        equipamentos = []
        for documento in consulta.stream():
            dados = documento.to_dict()
            dados["id"] = documento.id
            equipamentos.append(dados)
        return equipamentos

    def buscar(self, equipamento_id):
        documento = self.collection.document(equipamento_id).get()
        if not documento.exists:
            return None
        dados = documento.to_dict()
        dados["id"] = documento.id
        return dados

    def atualizar(self, equipamento_id, dados):
        self.collection.document(equipamento_id).update({
            **dados,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

    def excluir(self, equipamento_id):
        self.collection.document(equipamento_id).update({
            "ativo": False,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })
