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

        api_key = os.environ.get("FIREBASE_WEB_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("FIREBASE_WEB_API_KEY")
            except Exception:
                api_key = None
        if not api_key:
            raise RuntimeError("FIREBASE_WEB_API_KEY não configurada.")

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

        api_key = os.environ.get("FIREBASE_WEB_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("FIREBASE_WEB_API_KEY")
            except Exception:
                api_key = None
        if not api_key:
            raise RuntimeError("FIREBASE_WEB_API_KEY não configurada.")

        resposta = self.http_client.post(
            "https://identitytoolkit.googleapis.com/v1/accounts:signUp",
            params={"key": api_key},
            json={"email": email, "password": senha, "returnSecureToken": True},
            timeout=10,
        )
        if resposta.status_code != 200:
            raise ValueError("Não foi possível criar a conta. Verifique os dados e tente novamente.")

        dados = resposta.json()
        usuario_id = self.usuario_model.criar(nome, email, ra, perfil, dados["localId"])
        return {"id": usuario_id, "id_token": dados.get("idToken")}
