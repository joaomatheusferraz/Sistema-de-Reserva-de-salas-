import streamlit as st


SESSION_USER_KEY = "usuario_autenticado"
SESSION_TOKEN_KEY = "firebase_id_token"


def iniciar_sessao(usuario, id_token=None):
    st.session_state[SESSION_USER_KEY] = usuario
    if id_token:
        st.session_state[SESSION_TOKEN_KEY] = id_token


def usuario_atual():
    return st.session_state.get(SESSION_USER_KEY)


def autenticado():
    return usuario_atual() is not None


def exigir_autenticacao():
    if not autenticado():
        raise PermissionError("Usuário não autenticado.")
    return usuario_atual()


def encerrar_sessao():
    """Limpa todas as chaves da sessão para evitar vazamento de estado entre logins."""
    for chave in list(st.session_state.keys()):
        st.session_state.pop(chave, None)
