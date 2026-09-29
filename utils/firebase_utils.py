import json
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore


def _normalizar_credencial(cred_info):
    """Converte a configuração em dict e corrige quebras de linha da chave."""
    cred_info = dict(cred_info)
    private_key = cred_info.get("private_key")
    if isinstance(private_key, str):
        cred_info["private_key"] = private_key.replace("\\n", "\n")
    return cred_info


def _credencial_dos_secrets_streamlit():
    """Lê a conta de serviço configurada nos Secrets do Streamlit Cloud."""
    try:
        import streamlit as st

        service_account_json = st.secrets.get("FIREBASE_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            return _normalizar_credencial(json.loads(service_account_json))

        service_account = st.secrets.get("firebase_service_account")
        if service_account:
            return _normalizar_credencial(service_account)
    except Exception:
        # Fora do Streamlit, ou sem arquivo de secrets, tenta as demais fontes.
        return None

    return None


def _carregar_credencial():
    service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if service_account_json:
        return credentials.Certificate(
            _normalizar_credencial(json.loads(service_account_json))
        )

    cred_info = _credencial_dos_secrets_streamlit()
    if cred_info:
        return credentials.Certificate(cred_info)

    caminho_local = Path(__file__).resolve().parents[1] / "secrets" / "key.json"
    if caminho_local.is_file():
        return credentials.Certificate(str(caminho_local))

    raise RuntimeError(
        "Credenciais do Firebase não configuradas. No Streamlit Cloud, abra "
        "Manage app > Settings > Secrets e configure a seção "
        "[firebase_service_account]."
    )


def init_firestore():
    if not firebase_admin._apps:
        firebase_admin.initialize_app(_carregar_credencial())

    return firestore.client()
