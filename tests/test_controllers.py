import unittest

from controllers.auth_controller import AuthController
from controllers.reserva_controller import ReservaController


class FakeReservaService:

    def __init__(self):
        self.reservas = {"res_1": {"id": "res_1", "status": "pendente"}}

    def criar(self, espaco_id, responsavel_id, inicio, fim, finalidade, perfil):
        if not espaco_id:
            raise ValueError("Informe o espaço da reserva.")
        if perfil == "aluno":
            raise PermissionError("Aluno não pode reservar.")
        return "res_nova"

    def buscar(self, reserva_id):
        return self.reservas.get(reserva_id)

    def listar_do_responsavel(self, responsavel_id):
        return list(self.reservas.values())

    def listar_pendentes(self, perfil):
        if perfil != "coordenador":
            raise PermissionError("Apenas coordenador pode listar pendentes.")
        return list(self.reservas.values())

    def listar_todas(self, perfil):
        if perfil != "coordenador":
            raise PermissionError("Apenas coordenador pode listar todas.")
        return list(self.reservas.values())

    def historico_da_reserva(self, reserva_id, perfil):
        return [{"acao": "criacao"}]

    def listar_calendario(self):
        return [{"id": "cal_1"}]

    def aprovar(self, reserva_id, coordenador_id, perfil):
        if perfil != "coordenador":
            raise PermissionError("Sem permissão.")
        self.reservas[reserva_id]["status"] = "reservada"

    def rejeitar(self, reserva_id, coordenador_id, perfil, motivo=None):
        if not motivo:
            raise ValueError("Motivo obrigatório.")
        self.reservas[reserva_id]["status"] = "rejeitada"

    def cancelar(self, reserva_id, responsavel_id, perfil):
        self.reservas[reserva_id]["status"] = "cancelada"

    def editar(self, reserva_id, responsavel_id, perfil, dados):
        self.reservas[reserva_id].update(dados)


class FakeAuthService:

    def login_por_ra(self, ra, senha):
        if ra == "erro":
            raise ValueError("Credenciais inválidas.")
        return {"id_token": "token123", "usuario": {"id": "u1", "nome": "User", "perfil": "professor"}}

    def registrar_usuario(self, nome, email, ra, senha, perfil="aluno"):
        if not nome:
            raise ValueError("Nome obrigatório.")
        return {"id": "u_new", "nome": nome}

    def enviar_redefinicao_senha(self, ra):
        if not ra:
            raise ValueError("Informe o RA.")


class TestControllers(unittest.TestCase):

    def setUp(self):
        self.service = FakeReservaService()
        self.controller = ReservaController(self.service)

    def test_criar_reserva_sucesso_e_erros(self):
        sucesso, res = self.controller.criar_reserva("e1", "u1", "ini", "fim", "aula", "professor")
        self.assertTrue(sucesso)
        self.assertEqual(res, "res_nova")

        sucesso_erro, msg = self.controller.criar_reserva("", "u1", "ini", "fim", "aula", "professor")
        self.assertFalse(sucesso_erro)
        self.assertIn("espaço", msg.lower())

        sucesso_perm, msg_perm = self.controller.criar_reserva("e1", "u1", "ini", "fim", "aula", "aluno")
        self.assertFalse(sucesso_perm)
        self.assertIn("aluno", msg_perm.lower())

    def test_buscar_reserva(self):
        sucesso, dados = self.controller.buscar_reserva("res_1")
        self.assertTrue(sucesso)
        self.assertEqual(dados["status"], "pendente")

        sucesso_nf, _ = self.controller.buscar_reserva("inexistente")
        self.assertFalse(sucesso_nf)

    def test_aprovar_rejeitar_cancelar_reserva(self):
        ok, _ = self.controller.aprovar_reserva("res_1", "coord1", "coordenador")
        self.assertTrue(ok)

        ok_rej, _ = self.controller.rejeitar_reserva("res_1", "coord1", "coordenador", motivo="Motivo")
        self.assertTrue(ok_rej)

        ok_canc, _ = self.controller.cancelar_reserva("res_1", "u1", "professor")
        self.assertTrue(ok_canc)

    def test_listar_e_historico(self):
        self.assertEqual(len(self.controller.listar_reservas_do_responsavel("u1")), 1)
        self.assertEqual(len(self.controller.listar_pendentes("coordenador")), 1)
        self.assertEqual(len(self.controller.listar_todas("coordenador")), 1)
        self.assertEqual(len(self.controller.historico_da_reserva("res_1", "coordenador")), 1)
        self.assertEqual(len(self.controller.listar_calendario()), 1)

    def test_auth_controller(self):
        fake_auth = FakeAuthService()
        auth_ctrl = AuthController(service=fake_auth)

        ok, msg = auth_ctrl.login("2026123", "senha123")
        self.assertTrue(ok)

        ok_err, _ = auth_ctrl.login("erro", "senha123")
        self.assertFalse(ok_err)

        ok_reg, _ = auth_ctrl.registrar("Nome", "email@teste.com", "2026123", "123456", "aluno")
        self.assertTrue(ok_reg)

        ok_reset, _ = auth_ctrl.esqueci_senha("2026123")
        self.assertTrue(ok_reset)


if __name__ == "__main__":
    unittest.main()
