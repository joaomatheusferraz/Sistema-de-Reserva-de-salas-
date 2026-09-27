from firebase_admin import firestore

from utils.firebase_utils import init_firestore


class ReservaModel:

    def __init__(self):
        self.db = init_firestore()
        self.collection = self.db.collection("reservas")

    def criar(self, dados):
        agora = firestore.SERVER_TIMESTAMP
        documento = {
            **dados,
            "created_at": agora,
            "updated_at": agora,
        }
        return self.collection.add(documento)[1].id

    def buscar(self, reserva_id):
        documento = self.collection.document(reserva_id).get()
        if not documento.exists:
            return None
        dados = documento.to_dict()
        dados["id"] = documento.id
        return dados

    def listar_por_responsavel(self, responsavel_id):
        reservas = []
        consulta = self.collection.where(
            "responsavel_id", "==", responsavel_id
        )
        for documento in consulta.stream():
            dados = documento.to_dict()
            dados["id"] = documento.id
            reservas.append(dados)
        return reservas
