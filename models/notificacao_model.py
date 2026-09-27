from firebase_admin import firestore

from utils.firebase_utils import init_firestore


class NotificacaoModel:

    def __init__(self):
        self.collection = init_firestore().collection("notificacoes")

    def criar(self, dados):
        documento = {
            **dados,
            "lida": False,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        return self.collection.add(documento)[1].id

    def listar_do_usuario(self, usuario_id, apenas_nao_lidas=False):
        consulta = self.collection.where("usuario_id", "==", usuario_id)
        if apenas_nao_lidas:
            consulta = consulta.where("lida", "==", False)

        notificacoes = []
        for documento in consulta.stream():
            dados = documento.to_dict()
            dados["id"] = documento.id
            notificacoes.append(dados)
        return notificacoes

    def marcar_como_lida(self, notificacao_id):
        self.collection.document(notificacao_id).update({"lida": True})
