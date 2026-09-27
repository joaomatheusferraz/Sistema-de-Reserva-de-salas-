import streamlit as st

from controllers.auth_controller import AuthController
from utils.session import autenticado, usuario_atual
from views.calendario_view import calendario_view
from views.coordenador_view import coordenador_view
from views.espacos_view import espacos_view
from views.home_view import home_view
from views.login_view import login_view
from views.reservas_view import reservas_view


st.set_page_config(page_title="UniReserve", page_icon="🏫", layout="wide")


def app():
    if not autenticado():
        login_view()
        return

    usuario = usuario_atual()
    st.sidebar.title("UniReserve")
    st.sidebar.caption(usuario.get("nome", "Usuário"))
    pagina = st.sidebar.radio(
        "Navegação",
        ["Início", "Espaços", "Reservas", "Calendário"]
        + (["Coordenação"] if usuario.get("perfil") == "coordenador" else []),
    )

    if st.sidebar.button("Sair"):
        AuthController.logout()
        st.rerun()

    if pagina == "Início":
        home_view(usuario)
    elif pagina == "Espaços":
        espacos_view()
    elif pagina == "Reservas":
        reservas_view(usuario)
    elif pagina == "Calendário":
        calendario_view(usuario)
    else:
        coordenador_view(usuario)


app()
