"""Controlador de reservas de salas e laboratórios."""

from services.reserva_service import ReservaService


class ReservaController:
    """Gerencia solicitações, aprovações, cancelamentos e consultas de reservas."""

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
        """Cria uma nova solicitação ou reserva direta dependendo do perfil."""
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
        """Busca os detalhes de uma reserva pelo ID."""
        try:
            reserva = self.service.buscar(reserva_id)
            if not reserva:
                return False, "Reserva não encontrada."
            return True, reserva
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def listar_reservas_do_responsavel(self, responsavel_id):
        """Lista todas as reservas associadas a um responsável."""
        try:
            return self.service.listar_do_responsavel(responsavel_id)
        except (ValueError, TypeError) as erro:
            return False, str(erro)

    def listar_pendentes(self, perfil):
        """Lista reservas pendentes aguardando aprovação do coordenador."""
        try:
            return self.service.listar_pendentes(perfil)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def listar_todas(self, perfil):
        """Lista todo o histórico de reservas para visualização administrativa."""
        try:
            return self.service.listar_todas(perfil)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def historico_da_reserva(self, reserva_id, perfil):
        """Obtém o histórico de eventos de ciclo de vida de uma reserva."""
        try:
            return self.service.historico_da_reserva(reserva_id, perfil)
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def listar_calendario(self):
        """Lista reservas e bloqueios para renderização na agenda pública."""
        try:
            return self.service.listar_calendario()
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def aprovar_reserva(self, reserva_id, coordenador_id, perfil):
        """Aprova uma solicitação de reserva pendente."""
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
        """Rejeita uma solicitação de reserva pendente com justificativa opcional."""
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
        """Cancela uma reserva existente pelo responsável ou coordenador."""
        try:
            self.service.cancelar(reserva_id, responsavel_id, perfil)
            return True, "Reserva cancelada com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)

    def editar_reserva(self, reserva_id, responsavel_id, perfil, dados):
        """Atualiza horário, espaço ou finalidade de uma reserva."""
        try:
            self.service.editar(reserva_id, responsavel_id, perfil, dados)
            return True, "Reserva atualizada com sucesso!"
        except (ValueError, TypeError, PermissionError) as erro:
            return False, str(erro)
