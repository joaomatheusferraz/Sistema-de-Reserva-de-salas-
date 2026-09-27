from services.auth_service import AuthService
from utils.session import encerrar_sessao, iniciar_sessao


class AuthController:

    def __init__(self, service=None):
        self.service = service or AuthService()

    def login(self, ra, senha):
        try:
            resultado = self.service.login_por_ra(ra, senha)
            iniciar_sessao(
                resultado["usuario"],
                resultado["id_token"],
            )
            return True, "Login realizado com sucesso."
        except (ValueError, PermissionError, RuntimeError):
            return False, "Não foi possível realizar o login."

    def validar_token(self, id_token):
        try:
            usuario = self.service.autenticar_token(id_token)
            iniciar_sessao(usuario, id_token)
            return True, usuario
        except (ValueError, PermissionError):
            return False, "Sessão inválida."

    @staticmethod
    def logout():
        encerrar_sessao()
