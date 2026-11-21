import unittest

from controllers.espaco_controller import EspacoController
from domain.enums import TipoEspaco
from services.espaco_service import EspacoService


class FakeEspacoModel:

    def __init__(self):
        self.espacos = {}

    def criar(self, dados):
        doc_id = f"espaco_{len(self.espacos) + 1}"
        self.espacos[doc_id] = {**dados, "id": doc_id, "ativo": True}
        return doc_id

    def listar(self, apenas_ativos=True):
        if apenas_ativos:
            return [e for e in self.espacos.values() if e.get("ativo", True)]
        return list(self.espacos.values())

    def buscar(self, espaco_id):
        return self.espacos.get(espaco_id)

    def atualizar(self, espaco_id, dados):
        if espaco_id in self.espacos:
            self.espacos[espaco_id].update(dados)

    def excluir(self, espaco_id):
        if espaco_id in self.espacos:
            self.espacos[espaco_id]["ativo"] = False


class TestEspacoServiceEController(unittest.TestCase):

    def setUp(self):
        self.model = FakeEspacoModel()
        self.service = EspacoService(self.model)
        self.controller = EspacoController(self.service)

    def test_criar_espaco_com_sucesso(self):
        espaco_id = self.service.criar(
            nome="Laboratório de Informática 1",
            tipo=TipoEspaco.LABORATORIO.value,
            capacidade=40,
            localizacao={"bloco": "B", "andar": "1"},
        )
        self.assertTrue(espaco_id.startswith("espaco_"))
        salvo = self.service.buscar(espaco_id)
        self.assertEqual(salvo["nome"], "Laboratório de Informática 1")
        self.assertEqual(salvo["capacidade"], 40)
        self.assertTrue(salvo["ativo"])

    def test_validar_nome_obrigatorio(self):
        with self.assertRaises(ValueError) as ctx:
            self.service.criar("", TipoEspaco.SALA.value, 30)
        self.assertIn("nome", str(ctx.exception).lower())

    def test_validar_tipo_espaco(self):
        with self.assertRaises(ValueError) as ctx:
            self.service.criar("Sala 101", "auditorio_invalido", 30)
        self.assertIn("tipo de espaço inválido", str(ctx.exception).lower())

    def test_validar_capacidade_positiva(self):
        with self.assertRaises(ValueError) as ctx:
            self.service.criar("Sala 101", TipoEspaco.SALA.value, 0)
        self.assertIn("inteiro positivo", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            self.service.criar("Sala 101", TipoEspaco.SALA.value, -5)
        self.assertIn("inteiro positivo", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            self.service.criar("Sala 101", TipoEspaco.SALA.value, "trinta")
        self.assertIn("inteiro positivo", str(ctx.exception).lower())

    def test_atualizar_e_excluir_espaco(self):
        espaco_id = self.service.criar("Sala 201", TipoEspaco.SALA.value, 25)
        self.service.atualizar(espaco_id, {
            "nome": "Sala 201 Atualizada",
            "tipo": TipoEspaco.SALA.value,
            "capacidade": 30,
        })
        salvo = self.service.buscar(espaco_id)
        self.assertEqual(salvo["nome"], "Sala 201 Atualizada")
        self.assertEqual(salvo["capacidade"], 30)

        self.service.excluir(espaco_id)
        salvo_excluido = self.service.buscar(espaco_id)
        self.assertFalse(salvo_excluido["ativo"])
        self.assertEqual(len(self.service.listar(apenas_ativos=True)), 0)

    def test_controller_espaco(self):
        sucesso, res = self.controller.criar_espaco(
            nome="Auditório Principal",
            tipo=TipoEspaco.SALA.value,
            capacidade=100,
        )
        self.assertTrue(sucesso)
        self.assertTrue(res.startswith("espaco_"))

        sucesso_erro, msg_erro = self.controller.criar_espaco(
            nome="",
            tipo=TipoEspaco.SALA.value,
            capacidade=100,
        )
        self.assertFalse(sucesso_erro)

        sucesso_del, msg_del = self.controller.excluir_espaco("espaco_1")
        self.assertTrue(sucesso_del)

    def test_rbac_coordenador_espaco(self):
        with self.assertRaises(PermissionError):
            self.service.criar("Sala X", TipoEspaco.SALA.value, 20, perfil="aluno")

        with self.assertRaises(PermissionError):
            self.service.atualizar("espaco_1", {"nome": "Novo", "tipo": TipoEspaco.SALA.value, "capacidade": 20}, perfil="professor")

        with self.assertRaises(PermissionError):
            self.service.excluir("espaco_1", perfil="externo")


if __name__ == "__main__":
    unittest.main()
