from utils.firebase_utils import init_firestore


class UsuarioModel:

    def __init__(self):
        self.db = init_firestore()
        self.collection = self.db.collection("usuarios")

    def criar(self, nome, email):
        documento = {
            "nome": nome,
            "email": email
        }

        doc_ref = self.collection.add(documento)

        return doc_ref