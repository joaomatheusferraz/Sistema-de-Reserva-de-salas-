from utils.firebase_utils import init_firestore


class UsuarioModel:

    def __init__(self):
        self.db = init_firestore()
        self.collection = self.db.collection("usuarios")

    # CREATE
    def criar(self, nome, email):

        documento = {
            "nome": nome,
            "email": email
        }

        doc_ref = self.collection.add(documento)

        return doc_ref[1].id

    # READ
    def listar(self):

        documentos = self.collection.stream()

        usuarios = []

        for documento in documentos:

            dados = documento.to_dict()

            usuarios.append({
                "id": documento.id,
                "nome": dados.get("nome"),
                "email": dados.get("email")
            })

        return usuarios

    # UPDATE
    def atualizar(self, usuario_id, nome, email):

        documento = {
            "nome": nome,
            "email": email
        }

        self.collection.document(usuario_id).update(documento)

    # DELETE
    def excluir(self, usuario_id):

        self.collection.document(usuario_id).delete()