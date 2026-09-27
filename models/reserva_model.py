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

    def criar_se_disponivel(self, dados):
        inicio = dados["inicio"]
        fim = dados["fim"]
        espaco_id = dados["espaco_id"]
        transacao = self.db.transaction()

        @firestore.transactional
        def executar(transacao):
            reservas_query = self.collection.where(
                "espaco_id", "==", espaco_id
            ).where(
                "status", "in", ["pendente", "reservada"]
            )
            reservas = transacao.get(reservas_query)
            for reserva in reservas:
                reserva_dados = reserva.to_dict()
                if self._sobrepoe(
                    inicio,
                    fim,
                    reserva_dados.get("inicio"),
                    reserva_dados.get("fim"),
                ):
                    raise ValueError("O espaço já está ocupado nesse período.")

            bloqueios_query = self.db.collection("bloqueios").where(
                "espaco_id", "==", espaco_id
            ).where("ativo", "==", True)
            bloqueios = transacao.get(bloqueios_query)
            for bloqueio in bloqueios:
                bloqueio_dados = bloqueio.to_dict()
                if self._sobrepoe(
                    inicio,
                    fim,
                    bloqueio_dados.get("inicio"),
                    bloqueio_dados.get("fim"),
                ):
                    raise ValueError("O espaço está bloqueado nesse período.")

            documento = {
                **dados,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
            referencia = self.collection.document()
            transacao.create(referencia, documento)
            return referencia.id

        return executar(transacao)

    @staticmethod
    def _sobrepoe(inicio_novo, fim_novo, inicio_existente, fim_existente):
        if inicio_existente is None or fim_existente is None:
            return False
        return (
            inicio_novo < fim_existente
            and fim_novo > inicio_existente
        )

    def buscar(self, reserva_id):
        documento = self.collection.document(reserva_id).get()
        if not documento.exists:
            return None
        dados = documento.to_dict()
        dados["id"] = documento.id
        return dados

    def atualizar_status(self, reserva_id, dados):
        self.collection.document(reserva_id).update({
            **dados,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

    def atualizar_se_disponivel(self, reserva_id, dados):
        transacao = self.db.transaction()
        referencia = self.collection.document(reserva_id)

        @firestore.transactional
        def executar(transacao):
            atual = transacao.get(referencia)
            if not atual.exists:
                raise ValueError("Reserva não encontrada.")

            reservas_query = self.collection.where(
                "espaco_id", "==", dados["espaco_id"]
            ).where(
                "status", "in", ["pendente", "reservada"]
            )
            reservas = transacao.get(reservas_query)
            for reserva in reservas:
                if reserva.id == reserva_id:
                    continue
                reserva_dados = reserva.to_dict()
                if self._sobrepoe(
                    dados["inicio"],
                    dados["fim"],
                    reserva_dados.get("inicio"),
                    reserva_dados.get("fim"),
                ):
                    raise ValueError("O espaço já está ocupado nesse período.")

            bloqueios_query = self.db.collection("bloqueios").where(
                "espaco_id", "==", dados["espaco_id"]
            ).where("ativo", "==", True)
            bloqueios = transacao.get(bloqueios_query)
            for bloqueio in bloqueios:
                bloqueio_dados = bloqueio.to_dict()
                if self._sobrepoe(
                    dados["inicio"],
                    dados["fim"],
                    bloqueio_dados.get("inicio"),
                    bloqueio_dados.get("fim"),
                ):
                    raise ValueError("O espaço está bloqueado nesse período.")

            transacao.update(referencia, {
                **dados,
                "updated_at": firestore.SERVER_TIMESTAMP,
            })

        executar(transacao)

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
