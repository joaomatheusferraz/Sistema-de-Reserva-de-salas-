import streamlit as st

from controllers.auth_controller import AuthController
from utils.session import autenticado, usuario_atual
from utils.ui import normalizar_perfil, perfil_badge, registrar_paginas
from views.calendario_view import calendario_view
from views.coordenador_view import coordenador_view
from views.espacos_view import espacos_view
from views.home_view import home_view
from views.login_view import login_view
from views.reservas_view import reservas_view


st.set_page_config(
    page_title="UniReserve",
    page_icon=":material/meeting_room:",
    layout="wide",
)


# Cada página é um callable sem argumentos; o usuário vem da sessão.
def pagina_inicio():
    home_view(usuario_atual())


def pagina_espacos():
    espacos_view(usuario_atual())


def pagina_reservas():
    reservas_view(usuario_atual())


def pagina_calendario():
    calendario_view(usuario_atual())


def pagina_coordenacao():
    coordenador_view(usuario_atual())


def sair():
    AuthController.logout()


def barra_lateral(usuario, perfil):
    with st.sidebar:
        with st.container(border=True, gap="xsmall"):
            st.markdown(f"**{usuario.get('nome', 'Usuário')}**")
            if usuario.get("email"):
                st.caption(usuario["email"])
            perfil_badge(perfil)
        st.button(
            "Sair",
            icon=":material/logout:",
            on_click=sair,
            width="stretch",
        )


def app():
    if not autenticado():
        st.navigation(
            [st.Page(login_view, title="Entrar", icon=":material/login:")],
            position="hidden",
        ).run()
        return

    usuario = usuario_atual()
    # Perfis são armazenados em minúsculas. Normalizar aqui evita que uma
    # conta criada manualmente como "Professor" perca a opção de reservar.
    perfil = normalizar_perfil(usuario)

    inicio = st.Page(pagina_inicio, title="Início", icon=":material/space_dashboard:", url_path="inicio", default=True)
    espacos = st.Page(pagina_espacos, title="Salas e espaços", icon=":material/meeting_room:", url_path="espacos")
    calendario = st.Page(pagina_calendario, title="Agenda", icon=":material/calendar_month:", url_path="calendario")
    disponiveis = {"inicio": inicio, "espacos": espacos, "calendario": calendario}

    paginas = {"": [inicio], "Salas": [espacos, calendario]}
    if perfil in {"professor", "externo"}:
        reservas = st.Page(pagina_reservas, title="Reservar sala", icon=":material/event_available:", url_path="reservas")
        paginas["Salas"].insert(0, reservas)
        disponiveis["reservas"] = reservas
    if perfil == "coordenador":
        coordenacao = st.Page(pagina_coordenacao, title="Coordenação", icon=":material/fact_check:", url_path="coordenacao")
        paginas["Gestão"] = [coordenacao]
        disponiveis["coordenacao"] = coordenacao
    registrar_paginas(disponiveis)

    pagina = st.navigation(paginas)
    barra_lateral(usuario, perfil)
    pagina.run()


app()
