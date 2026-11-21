import unittest

from controllers.equipamento_controller import EquipamentoController
from services.equipamento_service import EquipamentoService


class FakeEquipamentoModel:

    def __init__(self):
        self.equipamentos = {}

    def criar(self, dados):
        doc_id = f"equip_{len(self.equipamentos) + 1}"
        self.equipamentos[doc_id] = {**dados, "id": doc_id, "ativo": True}
        return doc_id

    def listar(self, apenas_ativos=True):
        if apenas_ativos:
            return [e for e in self.equipamentos.values() if e.get("ativo", True)]
        return list(self.equipamentos.values())

    def buscar(self, equipamento_id):
        return self.equipamentos.get(equipamento_id)

    def atualizar(self, equipamento_id, dados):
        if equipamento_id in self.equipamentos:
            self.equipamentos[equipamento_id].update(dados)

    def excluir(self, equipamento_id):
        if equipamento_id in self.equipamentos:
            self.equipamentos[equipamento_id]["ativo"] = False


class TestEquipamentoServiceEController(unittest.TestCase):

    def setUp(self):
        self.model = FakeEquipamentoModel()
        self.service = EquipamentoService(self.model)
        self.controller = EquipamentoController(self.service)

    def test_criar_equipamento_com_sucesso(self):
        eq_id = self.service.criar("Projetor 4K", "HDMI e Wi-Fi", exige_autorizacao=True)
        self.assertTrue(eq_id.startswith("equip_"))
        salvo = self.service.buscar(eq_id)
        self.assertEqual(salvo["nome"], "Projetor 4K")
        self.assertEqual(salvo["descricao"], "HDMI e Wi-Fi")
        self.assertTrue(salvo["exige_autorizacao"])
        self.assertTrue(salvo["ativo"])

    def test_validar_nome_obrigatorio(self):
        with self.assertRaises(ValueError) as ctx:
            self.service.criar("", "Sem nome")
        self.assertIn("nome", str(ctx.exception).lower())

    def test_atualizar_e_excluir_equipamento(self):
        eq_id = self.service.criar("Caixa de Som", "Bluetooth")
        self.service.atualizar(eq_id, {"nome": "Caixa de Som JBL", "descricao": "Potente"})
        salvo = self.service.buscar(eq_id)
        self.assertEqual(salvo["nome"], "Caixa de Som JBL")

        self.service.excluir(eq_id)
        self.assertFalse(self.service.buscar(eq_id)["ativo"])

    def test_controller_equipamento(self):
        sucesso, res = self.controller.criar_equipamento(nome="Microfone Sem Fio")
        self.assertTrue(sucesso)
        self.assertTrue(res.startswith("equip_"))

        sucesso_erro, msg = self.controller.criar_equipamento(nome="")
        self.assertFalse(sucesso_erro)

        sucesso_up, _ = self.controller.atualizar_equipamento("equip_1", {"nome": "Microfone Lapela"})
        self.assertTrue(sucesso_up)

        sucesso_del, _ = self.controller.excluir_equipamento("equip_1")
        self.assertTrue(sucesso_del)


if __name__ == "__main__":
    unittest.main()
