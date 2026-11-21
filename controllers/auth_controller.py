"""Controlador de autenticação e gerenciamento de sessão do usuário."""

from services.auth_service import AuthService
from utils.session import encerrar_sessao, iniciar_sessao


class AuthController:
    """Orquestra operações de login, cadastro, recuperação de senha e sessão."""

    def __init__(self, service=None):
        self.service = service or AuthService()

    def login(self, ra, senha):
        """Autentica o usuário por RA e senha e inicia a sessão local."""
        try:
            resultado = self.service.login_por_ra(ra, senha)
            iniciar_sessao(
                resultado["usuario"],
                resultado["id_token"],
            )
            return True, "Login realizado com sucesso."
        except (ValueError, PermissionError, RuntimeError) as erro:
            return False, str(erro)

    def registrar(self, nome, email, ra, senha, perfil="aluno"):
        """Registra um novo usuário no Firebase Auth e Firestore."""
        try:
            self.service.registrar_usuario(nome, email, ra, senha, perfil)
            return True, "Cadastro realizado com sucesso. Já é possível entrar."
        except (ValueError, PermissionError, RuntimeError) as erro:
            return False, str(erro)
        except Exception as erro:
            return False, f"Erro inesperado ao cadastrar: {erro}"

    def esqueci_senha(self, ra):
        """Dispara link de redefinição de senha para o e-mail cadastrado."""
        try:
            self.service.enviar_redefinicao_senha(ra)
            return True, (
                "Se o RA estiver cadastrado, enviamos um link para o e-mail "
                "da conta. Confira também a caixa de spam."
            )
        except (ValueError, PermissionError, RuntimeError) as erro:
            return False, str(erro)

    def validar_token(self, id_token):
        """Valida o token de autenticação e restaura a sessão."""
        try:
            usuario = self.service.autenticar_token(id_token)
            iniciar_sessao(usuario, id_token)
            return True, usuario
        except (ValueError, PermissionError):
            return False, "Sessão inválida."

    @staticmethod
    def logout():
        """Encerra a sessão do usuário no Streamlit."""
        encerrar_sessao()
