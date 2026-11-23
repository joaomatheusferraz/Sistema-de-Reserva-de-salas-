import os
import unittest
from datetime import datetime, timedelta

from services.auth_service import AuthService
from services.bloqueio_service import BloqueioService
from services.reserva_service import ReservaService


class FakeUserModel:

    def __init__(self, perfil="professor", autorizados=None):
        self.perfil = perfil
        self.autorizados = autorizados or []

    def buscar(self, usuario_id):
        return {
            "id": usuario_id,
            "ativo": True,
            "perfil": self.perfil,
            "espacos_autorizados_ids": self.autorizados,
        }

    def buscar_por_ra(self, ra):
        return {
            "id": "u1",
            "email": "usuario@example.com",
            "ativo": True,
        }


class FakeSpaceModel:

    def buscar(self, espaco_id):
        return {"id": espaco_id, "ativo": True}


class FakeHistory:

    def __init__(self):
        self.events = []

    def registrar(self, *args, **kwargs):
        self.events.append((args, kwargs))
        return "h1"


class FakeNotifications:

    def __init__(self):
        self.events = []

    def criar(self, *args):
        self.events.append(args)
        return "n1"


class FakeReservationModel:

    def __init__(self):
        self.data = {
            "r1": {
                "id": "r1",
                "responsavel_id": "u1",
                "espaco_id": "e1",
                "status": "pendente",
            }
        }

    def criar_se_disponivel(self, dados):
        self.data["r2"] = {**dados, "id": "r2"}
        return "r2"

    def buscar(self, reserva_id):
        return self.data.get(reserva_id)

    def listar_por_responsavel(self, responsavel_id):
        return [
            item for item in self.data.values()
            if item.get("responsavel_id") == responsavel_id
        ]

    def listar_por_status(self, status):
        return [item for item in self.data.values() if item.get("status") == status]

    def atualizar_status(self, reserva_id, dados):
        self.data[reserva_id].update(dados)

    def aprovar_se_disponivel(self, reserva_id, coordenador_id):
        self.data[reserva_id].update({
            "status": "reservada",
            "aprovacao_necessaria": False,
            "analisada_por_id": coordenador_id,
            "motivo_rejeicao": None,
        })

    def atualizar_se_disponivel(self, reserva_id, dados):
        self.data[reserva_id].update(dados)

    def listar_ativas(self):
        return [
            item for item in self.data.values()
            if item.get("status") in {"pendente", "reservada"}
        ]


class FakeBlockModel:

    def criar(self, dados):
        return "b1"

    def listar(self, apenas_ativos=True):
        return []

    def remover(self, bloqueio_id):
        return None


class FakeHttp:

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"idToken": "token", "refreshToken": "refresh"}

    def post(self, *args, **kwargs):
        return self.Response()


class ServiceTests(unittest.TestCase):

    def setUp(self):
        # Sempre no futuro: o serviço rejeita reservas em horários já passados (RN07).
        self.inicio = (datetime.now() + timedelta(days=1)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        self.fim = self.inicio + timedelta(hours=1)
        self.history = FakeHistory()
        self.notifications = FakeNotifications()
        self.reservation_model = FakeReservationModel()

    def make_reservation_service(self, user_model=None):
        return ReservaService(
            self.reservation_model,
            user_model or FakeUserModel(),
            FakeSpaceModel(),
            self.history,
            self.notifications,
        )

    def test_profiles_and_statuses(self):
        service = self.make_reservation_service()
        self.assertEqual(
            service.criar("e1", "u1", self.inicio, self.fim, "aula", "professor"),
            "r2",
        )
        self.assertEqual(self.reservation_model.data["r2"]["status"], "pendente")

        # RN26: reserva do coordenador já nasce confirmada, sem aprovação.
        coordinator = self.make_reservation_service(FakeUserModel("coordenador"))
        coordinator.criar(
            "e1", "u1", self.inicio, self.fim, "reuniao", "coordenador"
        )
        self.assertEqual(self.reservation_model.data["r2"]["status"], "reservada")
        self.assertFalse(self.reservation_model.data["r2"]["aprovacao_necessaria"])

        student = self.make_reservation_service(FakeUserModel("aluno"))
        with self.assertRaises(PermissionError):
            student.criar("e1", "u1", self.inicio, self.fim, "estudo", "aluno")

    def test_external_space_permission(self):
        service = self.make_reservation_service(FakeUserModel("externo", ["e2"]))
        with self.assertRaises(PermissionError):
            service.criar("e1", "u1", self.inicio, self.fim, "evento", "externo")

        # RN28: sem espaços autorizados, o externo não reserva nada.
        sem_autorizacao = self.make_reservation_service(FakeUserModel("externo"))
        with self.assertRaises(PermissionError):
            sem_autorizacao.criar("e1", "u1", self.inicio, self.fim, "evento", "externo")

        autorizado = self.make_reservation_service(FakeUserModel("externo", ["e1"]))
        autorizado.criar("e1", "u1", self.inicio, self.fim, "evento", "externo")
        self.assertEqual(self.reservation_model.data["r2"]["status"], "pendente")

    def test_students_can_consult_calendar_but_not_create(self):
        service = self.make_reservation_service(FakeUserModel("aluno"))
        self.assertEqual(len(service.listar_calendario()), 1)
        with self.assertRaises(PermissionError):
            service.criar("e1", "u1", self.inicio, self.fim, "estudo", "aluno")

    def test_overlap_rule_allows_adjacent_periods(self):
        from models.reserva_model import ReservaModel

        self.assertTrue(
            ReservaModel._sobrepoe(
                self.inicio,
                self.fim,
                self.inicio + timedelta(minutes=30),
                self.fim + timedelta(minutes=30),
            )
        )
        self.assertFalse(
            ReservaModel._sobrepoe(
                self.inicio,
                self.fim,
                self.fim,
                self.fim + timedelta(hours=1),
            )
        )

    def test_workflow_and_audit(self):
        service = self.make_reservation_service()
        service.aprovar("r1", "coord1", "coordenador")
        self.assertEqual(self.reservation_model.data["r1"]["status"], "reservada")

        self.reservation_model.data["r1"]["status"] = "pendente"
        service.rejeitar("r1", "coord1", "coordenador", "Conflito")
        self.assertEqual(self.reservation_model.data["r1"]["status"], "rejeitada")

        self.reservation_model.data["r1"]["status"] = "reservada"
        service.cancelar("r1", "u1", "professor")
        self.assertEqual(self.reservation_model.data["r1"]["status"], "cancelada")
        self.assertGreaterEqual(len(self.history.events), 3)
        self.assertGreaterEqual(len(self.notifications.events), 3)

    def test_rejection_requires_reason(self):
        service = self.make_reservation_service()
        with self.assertRaises(ValueError):
            service.rejeitar("r1", "coord1", "coordenador", "")

    def test_block_permission(self):
        service = BloqueioService(FakeBlockModel(), FakeSpaceModel(), self.history)
        service.criar("e1", self.inicio, self.fim, "Manutenção", "coord1", "coordenador")
        with self.assertRaises(PermissionError):
            service.criar("e1", self.inicio, self.fim, "Manutenção", "u1", "professor")

    def test_auth_login_uses_firebase_token(self):
        os.environ["FIREBASE_WEB_API_KEY"] = "test-key"
        service = AuthService(FakeUserModel(), FakeHttp())
        service.autenticar_token = lambda token: {
            "id": "u1",
            "perfil": "professor",
            "ativo": True,
        }
        result = service.login_por_ra("202600123", "senha")
        self.assertEqual(result["id_token"], "token")
        self.assertEqual(result["usuario"]["perfil"], "professor")

    def test_password_reset_sends_email_of_ra_owner(self):
        os.environ["FIREBASE_WEB_API_KEY"] = "test-key"
        chamadas = []

        class RecordingHttp(FakeHttp):
            def post(self, url, **kwargs):
                chamadas.append((url, kwargs["json"]))
                return self.Response()

        AuthService(FakeUserModel(), RecordingHttp()).enviar_redefinicao_senha(" 202600123 ")
        url, corpo = chamadas[0]
        self.assertTrue(url.endswith("accounts:sendOobCode"))
        self.assertEqual(
            corpo, {"requestType": "PASSWORD_RESET", "email": "usuario@example.com"}
        )

    def test_password_reset_unknown_ra_is_silent(self):
        class UnknownUserModel(FakeUserModel):
            def buscar_por_ra(self, ra):
                return None

        chamadas = []

        class RecordingHttp(FakeHttp):
            def post(self, *args, **kwargs):
                chamadas.append(args)
                return self.Response()

        AuthService(UnknownUserModel(), RecordingHttp()).enviar_redefinicao_senha("999")
        self.assertEqual(chamadas, [])
        with self.assertRaises(ValueError):
            AuthService(UnknownUserModel(), RecordingHttp()).enviar_redefinicao_senha("  ")


    def test_overlap_handles_firestore_timezones(self):
        from datetime import timezone
        from models.reserva_model import ReservaModel
        from utils.ui import FUSO_LOCAL, formatar_hora

        # 11:00 UTC = 08:00 em Brasília, como o Firestore devolve.
        existente_ini = datetime(2026, 11, 25, 11, 0, tzinfo=timezone.utc)
        existente_fim = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
        nova_ini = datetime(2026, 11, 25, 8, 30, tzinfo=FUSO_LOCAL)
        nova_fim = datetime(2026, 11, 25, 9, 30, tzinfo=FUSO_LOCAL)
        self.assertTrue(ReservaModel._sobrepoe(nova_ini, nova_fim, existente_ini, existente_fim))
        self.assertFalse(ReservaModel._sobrepoe(
            datetime(2026, 11, 25, 9, 0, tzinfo=FUSO_LOCAL),
            datetime(2026, 11, 25, 10, 0, tzinfo=FUSO_LOCAL),
            existente_ini, existente_fim,
        ))
        # Valores sem fuso (dados antigos) são tratados como UTC, sem TypeError.
        self.assertTrue(ReservaModel._sobrepoe(
            datetime(2026, 11, 25, 11, 30), datetime(2026, 11, 25, 12, 30),
            existente_ini, existente_fim,
        ))
        self.assertEqual(formatar_hora(existente_ini), "08:00")


    def test_teacher_cannot_edit_approved_reservation(self):
        service = self.make_reservation_service()
        self.reservation_model.data["r1"]["status"] = "reservada"
        dados = {"espaco_id": "e1", "inicio": self.inicio, "fim": self.fim, "finalidade": "aula"}
        with self.assertRaises(PermissionError):
            service.editar("r1", "u1", "professor", dados)
        self.reservation_model.data["r1"]["status"] = "pendente"
        service.editar("r1", "u1", "professor", dados)
        self.assertEqual(self.reservation_model.data["r1"]["finalidade"], "aula")

    def test_only_coordinator_lists_all_reservations(self):
        service = self.make_reservation_service()
        self.reservation_model.listar_todas = lambda: list(self.reservation_model.data.values())
        self.assertEqual(len(service.listar_todas("coordenador")), 1)
        with self.assertRaises(PermissionError):
            service.listar_todas("professor")

    def test_registration_profile_restriction_rn01(self):
        auth_service = AuthService(FakeUserModel(), FakeHttp())
        with self.assertRaises(ValueError) as ctx:
            auth_service.registrar_usuario("Prof", "prof@teste.com", "RA123", "senha123", perfil="professor")
        self.assertIn("coordenação", str(ctx.exception).lower())

    def test_operating_hours_validation_rn07(self):
        service = self.make_reservation_service()
        # Horário antes das 07:00
        madrugada_ini = self.inicio.replace(hour=6)
        madrugada_fim = self.inicio.replace(hour=7)
        with self.assertRaises(ValueError) as ctx:
            service.criar("e1", "u1", madrugada_ini, madrugada_fim, "aula", "professor")
        self.assertIn("07:00 e 23:00", str(ctx.exception))

    def test_block_conflict_detection_rn18(self):
        class ActiveReservationModel(FakeReservationModel):
            def listar_ativas(self):
                return [{
                    "id": "r_ativa",
                    "espaco_id": "e1",
                    "inicio": datetime(2026, 1, 1, 10, 0),
                    "fim": datetime(2026, 1, 1, 12, 0),
                    "status": "reservada",
                }]

        res_model = ActiveReservationModel()
        service = BloqueioService(FakeBlockModel(), FakeSpaceModel(), self.history, reserva_model=res_model)
        conflitos = service.verificar_reservas_conflitantes(
            "e1",
            datetime(2026, 1, 1, 11, 0),
            datetime(2026, 1, 1, 13, 0),
        )
        self.assertEqual(len(conflitos), 1)
        self.assertEqual(conflitos[0]["id"], "r_ativa")


if __name__ == "__main__":
    unittest.main()
