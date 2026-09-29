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

    def listar_pendentes(self, perfil):
        try:
            return self.service.listar_pendentes(perfil)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def listar_calendario(self):
        try:
            return self.service.listar_calendario()
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def aprovar_reserva(self, reserva_id, coordenador_id, perfil):
        try:
            self.service.aprovar(reserva_id, coordenador_id, perfil)
            return True, "Reserva aprovada com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def rejeitar_reserva(
        self,
        reserva_id,
        coordenador_id,
        perfil,
        motivo=None,
    ):
        try:
            self.service.rejeitar(
                reserva_id,
                coordenador_id,
                perfil,
                motivo,
            )
            return True, "Reserva rejeitada com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def cancelar_reserva(self, reserva_id, responsavel_id, perfil):
        try:
            self.service.cancelar(reserva_id, responsavel_id, perfil)
            return True, "Reserva cancelada com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def editar_reserva(self, reserva_id, responsavel_id, perfil, dados):
        try:
            self.service.editar(reserva_id, responsavel_id, perfil, dados)
            return True, "Reserva atualizada com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)
