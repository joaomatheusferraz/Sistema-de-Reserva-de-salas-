from models.usuario_model import UsuarioModel


class UsuarioController:

    def __init__(self):
        self.model = UsuarioModel()

    def cadastrar_usuario(self, nome, email):

        if not nome:
            return False, "Informe o nome."

        if not email:
            return False, "Informe o e-mail."

        try:
            self.model.criar(nome, email)

            return True, "Usuário cadastrado com sucesso!"

        except Exception as erro:
            return False, f"Erro ao cadastrar usuário: {erro}"