from models.usuario_model import UsuarioModel
from domain.enums import Perfil
from utils.validators import validar_email


class UsuarioController:

    def __init__(self):
        self.model = UsuarioModel()

    def cadastrar_usuario(self, nome, email, ra=None, perfil=Perfil.ALUNO.value):

        nome = nome.strip()
        email = email.strip()

        if not nome:
            return False, "Informe o nome."

        if not email:
            return False, "Informe o e-mail."
        if not validar_email(email):
            return False, "Informe um e-mail válido."
        if perfil not in {item.value for item in Perfil}:
            return False, "Perfil inválido."

        try:

            usuario_id = self.model.criar(nome, email, ra, perfil)

            return True, f"Usuário cadastrado! ID: {usuario_id}"

        except Exception as erro:

            return False, f"Erro ao cadastrar usuário: {erro}"

    def listar_usuarios(self):

        try:

            return self.model.listar()

        except Exception as erro:

            print(f"Erro ao listar usuários: {erro}")

            return []

    def atualizar_usuario(
        self,
        usuario_id,
        nome,
        email,
        ra=None,
        perfil=Perfil.ALUNO.value,
        ativo=True,
    ):

        nome = nome.strip()
        email = email.strip()

        if not nome:
            return False, "Informe o nome."

        if not email:
            return False, "Informe o e-mail."
        if not validar_email(email):
            return False, "Informe um e-mail válido."
        if perfil not in {item.value for item in Perfil}:
            return False, "Perfil inválido."

        try:

            self.model.atualizar(
                usuario_id,
                nome,
                email,
                ra,
                perfil,
                ativo,
            )

            return True, "Usuário atualizado com sucesso!"

        except Exception as erro:

            return False, f"Erro ao atualizar usuário: {erro}"

    def excluir_usuario(self, usuario_id):

        try:

            self.model.excluir(usuario_id)

            return True, "Usuário excluído com sucesso!"

        except Exception as erro:

            return False, f"Erro ao excluir usuário: {erro}"
