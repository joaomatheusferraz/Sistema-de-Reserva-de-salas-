from services.reserva_service import ReservaService


class ReservaController:

    def __init__(self, service=None):
        self.service = service or ReservaService()

    def criar_reserva(
        self,
        espaco_id,
        responsavel_id,
        inicio,
        fim,
        finalidade,
        perfil,
    ):
        try:
            reserva_id = self.service.criar(
                espaco_id,
                responsavel_id,
                inicio,
                fim,
                finalidade,
                perfil,
            )
            return True, reserva_id
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def buscar_reserva(self, reserva_id):
        try:
            return self.service.buscar(reserva_id)
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def listar_reservas_do_responsavel(self, responsavel_id):
        try:
            return self.service.listar_do_responsavel(responsavel_id)
        except (ValueError, TypeError) as erro:
            return False, str(erro)
