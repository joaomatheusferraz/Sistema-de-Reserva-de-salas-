import os

import requests
from firebase_admin import auth

from models.usuario_model import UsuarioModel


class AuthService:

    def __init__(self, usuario_model=None, http_client=None):
        self.usuario_model = usuario_model or UsuarioModel()
        self.http_client = http_client or requests

    def autenticar_token(self, id_token):
        if not id_token or not isinstance(id_token, str):
            raise ValueError("Token de autenticação não informado.")

        try:
            token = auth.verify_id_token(id_token)
        except Exception as erro:
            raise PermissionError("Token de autenticação inválido.") from erro

        usuario = self.usuario_model.buscar_por_uid(token["uid"])
        if not usuario or not usuario.get("ativo", True):
            raise PermissionError("Usuário não encontrado ou inativo.")

        return usuario

    def login_por_ra(self, ra, senha):
        ra = ra.strip() if isinstance(ra, str) else ""
        if not ra or not senha:
            raise ValueError("Informe o RA e a senha.")

        usuario = self.usuario_model.buscar_por_ra(ra)
        if not usuario or not usuario.get("ativo", True):
            raise PermissionError("RA ou senha inválidos.")

        api_key = self._api_key()

        resposta = self.http_client.post(
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
            params={"key": api_key},
            json={
                "email": usuario["email"],
                "password": senha,
                "returnSecureToken": True,
            },
            timeout=10,
        )
        if resposta.status_code != 200:
            raise PermissionError("RA ou senha inválidos.")

        dados = resposta.json()
        usuario_autenticado = self.autenticar_token(dados["idToken"])
        return {
            "usuario": usuario_autenticado,
            "id_token": dados["idToken"],
            "refresh_token": dados.get("refreshToken"),
        }

    def registrar_usuario(self, nome, email, ra, senha, perfil="aluno"):
        nome = nome.strip() if isinstance(nome, str) else ""
        email = email.strip() if isinstance(email, str) else ""
        ra = ra.strip() if isinstance(ra, str) else ""
        if not nome or not email or not ra or not senha:
            raise ValueError("Preencha nome, e-mail, RA e senha.")
        if perfil not in {"aluno", "professor", "externo"}:
            raise ValueError("Perfil de cadastro inválido.")
        if self.usuario_model.buscar_por_ra(ra):
            raise ValueError("Já existe um usuário cadastrado com esse RA.")

        api_key = self._api_key()

        try:
            resposta = self.http_client.post(
                "https://identitytoolkit.googleapis.com/v1/accounts:signUp",
                params={"key": api_key},
                json={"email": email, "password": senha, "returnSecureToken": True},
                timeout=10,
            )
        except Exception as erro:
            raise RuntimeError("Não foi possível conectar ao Firebase Authentication.") from erro

        if resposta.status_code != 200:
            raise ValueError(self._mensagem_erro_firebase(resposta))

        dados = resposta.json()
        uid = dados["localId"]
        try:
            usuario_id = self.usuario_model.criar(nome, email, ra, perfil, uid)
        except Exception as erro:
            # Desfaz a conta no Authentication para não deixar um e-mail
            # "preso" (EMAIL_EXISTS) sem documento correspondente no Firestore.
            try:
                auth.delete_user(uid)
            except Exception:
                pass
            raise RuntimeError(f"Erro ao salvar o usuário no Firestore: {erro}") from erro

        return {"id": usuario_id, "id_token": dados.get("idToken")}

    def enviar_redefinicao_senha(self, ra):
        """Envia o e-mail de redefinição de senha do Firebase para o dono do RA.

        Não informa se o RA existe: a resposta é a mesma nos dois casos,
        para que a tela não sirva para descobrir quais RAs estão cadastrados.
        """
        ra = ra.strip() if isinstance(ra, str) else ""
        if not ra:
            raise ValueError("Informe o seu RA.")

        usuario = self.usuario_model.buscar_por_ra(ra)
        if not usuario or not usuario.get("ativo", True) or not usuario.get("email"):
            return

        api_key = self._api_key()
        try:
            resposta = self.http_client.post(
                "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode",
                params={"key": api_key},
                json={"requestType": "PASSWORD_RESET", "email": usuario["email"]},
                timeout=10,
            )
        except Exception as erro:
            raise RuntimeError("Não foi possível conectar ao Firebase Authentication.") from erro

        if resposta.status_code != 200:
            codigo = self._codigo_erro(resposta)
            if codigo == "EMAIL_NOT_FOUND":
                # Usuário existe no Firestore, mas não no Authentication.
                return
            if codigo.startswith("TOO_MANY_ATTEMPTS"):
                raise PermissionError("Muitas tentativas. Tente novamente mais tarde.")
            raise RuntimeError("Não foi possível enviar o e-mail de redefinição.")

    @staticmethod
    def _api_key():
        api_key = os.environ.get("FIREBASE_WEB_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("FIREBASE_WEB_API_KEY")
            except Exception:
                api_key = None
        if not api_key:
            raise RuntimeError("FIREBASE_WEB_API_KEY não configurada.")
        return api_key

    @staticmethod
    def _codigo_erro(resposta):
        try:
            return resposta.json().get("error", {}).get("message", "")
        except Exception:
            return ""

    @staticmethod
    def _mensagem_erro_firebase(resposta):
        try:
            codigo = resposta.json().get("error", {}).get("message", "")
        except Exception:
            codigo = ""

        mensagens = {
            "EMAIL_EXISTS": "Este e-mail já está cadastrado.",
            "INVALID_EMAIL": "E-mail inválido.",
            "OPERATION_NOT_ALLOWED": (
                "Cadastro por e-mail/senha desativado no Firebase. Ative em "
                "Authentication > Sign-in method > E-mail/senha."
            ),
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Muitas tentativas. Tente novamente mais tarde.",
            "API_KEY_INVALID": "FIREBASE_WEB_API_KEY inválida.",
        }
        if codigo.startswith("WEAK_PASSWORD"):
            return "A senha deve ter pelo menos 6 caracteres."
        if codigo.startswith("API key not valid"):
            return mensagens["API_KEY_INVALID"]
        return mensagens.get(
            codigo,
            f"Não foi possível criar a conta ({codigo or resposta.status_code}).",
        )
