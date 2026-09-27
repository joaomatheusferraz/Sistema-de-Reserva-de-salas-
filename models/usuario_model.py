from utils.firebase_utils import init_firestore
from firebase_admin import firestore


class UsuarioModel:

    def __init__(self):
        self.db = init_firestore()
        self.collection = self.db.collection("usuarios")

    # CREATE
    def criar(self, nome, email, ra=None, perfil="aluno"):

        documento = {
            "nome": nome,
            "email": email,
            "ra": ra,
            "perfil": perfil,
            "ativo": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
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
                "email": dados.get("email"),
                "ra": dados.get("ra"),
                "perfil": dados.get("perfil", "aluno"),
                "ativo": dados.get("ativo", True),
                "created_at": dados.get("created_at"),
                "updated_at": dados.get("updated_at")
            })

        return usuarios

    def buscar(self, usuario_id):
        documento = self.collection.document(usuario_id).get()
        if not documento.exists:
            return None
        dados = documento.to_dict()
        dados["id"] = documento.id
        return dados

    # UPDATE
    def atualizar(self, usuario_id, nome, email, ra=None, perfil="aluno", ativo=True):

        documento = {
            "nome": nome,
            "email": email,
            "ra": ra,
            "perfil": perfil,
            "ativo": ativo,
            "updated_at": firestore.SERVER_TIMESTAMP
        }

        self.collection.document(usuario_id).update(documento)

    # DELETE
    def excluir(self, usuario_id):

        self.collection.document(usuario_id).delete()
