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
        self.inicio = datetime(2026, 1, 1, 10, 0)
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

        coordinator = self.make_reservation_service(FakeUserModel("coordenador"))
        with self.assertRaises(PermissionError):
            coordinator.criar(
                "e1", "u1", self.inicio, self.fim, "reuniao", "coordenador"
            )

        student = self.make_reservation_service(FakeUserModel("aluno"))
        with self.assertRaises(PermissionError):
            student.criar("e1", "u1", self.inicio, self.fim, "estudo", "aluno")

    def test_external_space_permission(self):
        service = self.make_reservation_service(FakeUserModel("externo", ["e2"]))
        with self.assertRaises(PermissionError):
            service.criar("e1", "u1", self.inicio, self.fim, "evento", "externo")

        unrestricted = self.make_reservation_service(FakeUserModel("externo"))
        unrestricted.criar(
            "e1", "u1", self.inicio, self.fim, "evento", "externo"
        )
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


if __name__ == "__main__":
    unittest.main()
