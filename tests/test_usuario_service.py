import unittest

from controllers.usuario_controller import UsuarioController
from domain.enums import Perfil
from services.usuario_service import UsuarioService


class FakeUsuarioModel:

    def __init__(self):
        self.usuarios = {}

    def criar(self, nome, email, ra=None, perfil="aluno", uid=None):
        doc_id = uid or f"user_{len(self.usuarios) + 1}"
        self.usuarios[doc_id] = {
            "id": doc_id,
            "nome": nome,
            "email": email,
            "ra": ra,
            "perfil": perfil,
            "ativo": True,
            "espacos_autorizados_ids": [],
        }
        return doc_id

    def listar(self):
        return list(self.usuarios.values())

    def buscar(self, usuario_id):
        return self.usuarios.get(usuario_id)

    def buscar_por_ra(self, ra):
        for u in self.usuarios.values():
            if u.get("ra") == ra:
                return u
        return None

    def atualizar(self, usuario_id, nome, email, ra=None, perfil="aluno", ativo=True):
        if usuario_id in self.usuarios:
            self.usuarios[usuario_id].update({
                "nome": nome,
                "email": email,
                "ra": ra,
                "perfil": perfil,
                "ativo": ativo,
            })

    def atualizar_autorizacoes(self, usuario_id, espacos_ids):
        if usuario_id in self.usuarios:
            self.usuarios[usuario_id]["espacos_autorizados_ids"] = list(espacos_ids)

    def atualizar_contato(self, usuario_id, email, telefone, email_anterior=None):
        if usuario_id in self.usuarios:
            self.usuarios[usuario_id]["email"] = email
            self.usuarios[usuario_id]["telefone"] = telefone

    def excluir(self, usuario_id):
        if usuario_id in self.usuarios:
            del self.usuarios[usuario_id]


class TestUsuarioServiceEController(unittest.TestCase):

    def setUp(self):
        self.model = FakeUsuarioModel()
        self.service = UsuarioService(self.model)
        self.controller = UsuarioController(self.service)

    def test_cadastrar_usuario_com_sucesso(self):
        uid = self.service.cadastrar(
            "Maria Silva",
            "maria@universidade.edu.br",
            ra="20261001",
            perfil="aluno",
        )
        self.assertTrue(uid.startswith("user_"))
        salvo = self.service.buscar_por_id(uid)
        self.assertEqual(salvo["nome"], "Maria Silva")
        self.assertEqual(salvo["email"], "maria@universidade.edu.br")
        self.assertEqual(salvo["ra"], "20261001")
        self.assertEqual(salvo["perfil"], "aluno")
        self.assertTrue(salvo["ativo"])

    def test_cadastrar_usuario_validacoes_obrigatorias(self):
        with self.assertRaises(ValueError) as ctx:
            self.service.cadastrar("", "maria@teste.com")
        self.assertIn("nome", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            self.service.cadastrar("Maria", "")
        self.assertIn("e-mail", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            self.service.cadastrar("Maria", "email_invalido")
        self.assertIn("válido", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            self.service.cadastrar("Maria", "maria@teste.com", perfil="perfil_inexistente")
        self.assertIn("perfil inválido", str(ctx.exception).lower())

    def test_bloquear_ra_duplicado(self):
        self.service.cadastrar("Carlos", "carlos@teste.com", ra="RA12345")
        with self.assertRaises(ValueError) as ctx:
            self.service.cadastrar("Outro", "outro@teste.com", ra="RA12345")
        self.assertIn("já existe um usuário", str(ctx.exception).lower())

    def test_listar_usuarios_ativos_e_todos(self):
        u1 = self.service.cadastrar("Ativo", "ativo@teste.com")
        u2 = self.service.cadastrar("Inativo", "inativo@teste.com")
        self.service.atualizar(u2, "Inativo", "inativo@teste.com", ativo=False)

        todos = self.service.listar(apenas_ativos=False)
        self.assertEqual(len(todos), 2)

        ativos = self.service.listar(apenas_ativos=True)
        self.assertEqual(len(ativos), 1)
        self.assertEqual(ativos[0]["id"], u1)

    def test_buscar_por_ra_e_id(self):
        uid = self.service.cadastrar("Professor", "prof@teste.com", ra="PROF99", perfil="professor")
        self.assertEqual(self.service.buscar_por_ra("PROF99")["id"], uid)
        self.assertIsNone(self.service.buscar_por_ra("INEXISTENTE"))
        self.assertIsNone(self.service.buscar_por_ra(""))

    def test_atualizar_usuario_com_sucesso(self):
        uid = self.service.cadastrar("Original", "original@teste.com", ra="RA01")
        self.service.atualizar(uid, "Nome Editado", "editado@teste.com", ra="RA01", perfil="professor", ativo=True)
        atualizado = self.service.buscar_por_id(uid)
        self.assertEqual(atualizado["nome"], "Nome Editado")
        self.assertEqual(atualizado["email"], "editado@teste.com")
        self.assertEqual(atualizado["perfil"], "professor")

    def test_atualizar_autorizacoes_espacos(self):
        uid = self.service.cadastrar("Externo", "ext@teste.com", perfil="externo")
        self.service.atualizar_autorizacoes(uid, ["sala_1", "lab_2"])
        salvo = self.service.buscar_por_id(uid)
        self.assertEqual(salvo["espacos_autorizados_ids"], ["sala_1", "lab_2"])

        with self.assertRaises(TypeError):
            self.service.atualizar_autorizacoes(uid, "nao_e_uma_lista")

    def test_excluir_usuario(self):
        uid = self.service.cadastrar("Para Deletar", "del@teste.com")
        self.assertIsNotNone(self.service.buscar_por_id(uid))
        self.service.excluir(uid)
        self.assertIsNone(self.service.buscar_por_id(uid))

    def test_controller_retornos_padronizados(self):
        sucesso, msg = self.controller.cadastrar_usuario("João", "joao@teste.com", perfil=Perfil.ALUNO.value)
        self.assertTrue(sucesso)
        self.assertIn("Usuário cadastrado!", msg)

        sucesso_erro, msg_erro = self.controller.cadastrar_usuario("", "invalido")
        self.assertFalse(sucesso_erro)

        sucesso_busca, dados = self.controller.buscar_usuario("user_1")
        self.assertTrue(sucesso_busca)
        self.assertEqual(dados["nome"], "João")

        sucesso_up, _ = self.controller.atualizar_usuario("user_1", "João Atual", "joao@teste.com")
        self.assertTrue(sucesso_up)

        sucesso_aut, _ = self.controller.atualizar_autorizacoes("user_1", ["espaco_a"])
        self.assertTrue(sucesso_aut)

        sucesso_del, _ = self.controller.excluir_usuario("user_1")
        self.assertTrue(sucesso_del)

    def test_atualizar_contato_service_e_controller(self):
        uid = self.service.cadastrar("Contato Teste", "contato@teste.com")
        self.service.atualizar_contato(uid, "novo@teste.com", "(11) 98765-4321")
        salvo = self.service.buscar_por_id(uid)
        self.assertEqual(salvo["email"], "novo@teste.com")
        self.assertEqual(salvo["telefone"], "(11) 98765-4321")

        with self.assertRaises(ValueError):
            self.service.atualizar_contato(uid, "email_invalido", "11987654321")

        with self.assertRaises(ValueError):
            self.service.atualizar_contato(uid, "valido@teste.com", "123")  # telefone sem DDD

        usuario_dict = {"id": uid, "email": "novo@teste.com"}
        ok, msg = self.controller.atualizar_contato(usuario_dict, "outro@teste.com", "(11) 99999-8888")
        self.assertTrue(ok)
        self.assertIn("atualizados", msg.lower())

        ok_err, _ = self.controller.atualizar_contato(usuario_dict, "invalido", "11999998888")
        self.assertFalse(ok_err)


if __name__ == "__main__":
    unittest.main()
