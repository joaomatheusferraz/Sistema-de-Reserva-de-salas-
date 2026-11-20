import unittest

from services.historico_service import HistoricoService
from services.notificacao_service import NotificacaoService


class FakeHistoricoModel:

    def __init__(self):
        self.registros = []

    def criar(self, dados):
        doc_id = f"hist_{len(self.registros) + 1}"
        self.registros.append({**dados, "id": doc_id})
        return doc_id

    def listar_por_entidade(self, entidade, entidade_id):
        return [
            r for r in self.registros
            if r.get("entidade") == entidade and r.get("entidade_id") == entidade_id
        ]


class FakeNotificacaoModel:

    def __init__(self):
        self.notificacoes = {}

    def criar(self, dados):
        doc_id = f"notif_{len(self.notificacoes) + 1}"
        self.notificacoes[doc_id] = {**dados, "id": doc_id, "lida": False}
        return doc_id

    def listar_do_usuario(self, usuario_id, apenas_nao_lidas=False):
        itens = [n for n in self.notificacoes.values() if n.get("usuario_id") == usuario_id]
        if apenas_nao_lidas:
            itens = [n for n in itens if not n.get("lida", False)]
        return itens

    def marcar_como_lida(self, notificacao_id):
        if notificacao_id in self.notificacoes:
            self.notificacoes[notificacao_id]["lida"] = True


class TestHistoricoENotificacao(unittest.TestCase):

    def setUp(self):
        self.hist_model = FakeHistoricoModel()
        self.hist_service = HistoricoService(self.hist_model)

        self.notif_model = FakeNotificacaoModel()
        self.notif_service = NotificacaoService(self.notif_model)

    def test_historico_registrar_e_listar(self):
        hid = self.hist_service.registrar(
            entidade="reserva",
            entidade_id="res_123",
            acao="aprovacao",
            executado_por_id="coord_1",
            dados_novos={"status": "reservada"},
        )
        self.assertEqual(hid, "hist_1")
        itens = self.hist_service.listar_por_entidade("reserva", "res_123")
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0]["acao"], "aprovacao")

    def test_historico_validacoes(self):
        with self.assertRaises(ValueError):
            self.hist_service.registrar("", "res_1", "acao", "user_1")
        with self.assertRaises(ValueError):
            self.hist_service.registrar("reserva", "", "acao", "user_1")
        with self.assertRaises(ValueError):
            self.hist_service.registrar("reserva", "res_1", "", "user_1")

    def test_notificacao_criar_listar_e_marcar_lida(self):
        nid = self.notif_service.criar(
            usuario_id="prof_1",
            tipo="reserva_aprovada",
            mensagem="Sua reserva foi aprovada!",
            entidade_id="res_1",
        )
        self.assertEqual(nid, "notif_1")

        todas = self.notif_service.listar_do_usuario("prof_1")
        self.assertEqual(len(todas), 1)
        self.assertFalse(todas[0]["lida"])

        self.notif_service.marcar_como_lida("notif_1")
        nao_lidas = self.notif_service.listar_do_usuario("prof_1", apenas_nao_lidas=True)
        self.assertEqual(len(nao_lidas), 0)

    def test_notificacao_validacoes(self):
        with self.assertRaises(ValueError):
            self.notif_service.criar("", "tipo", "msg")
        with self.assertRaises(ValueError):
            self.notif_service.criar("u1", "", "msg")
        with self.assertRaises(ValueError):
            self.notif_service.criar("u1", "tipo", "")


if __name__ == "__main__":
    unittest.main()
