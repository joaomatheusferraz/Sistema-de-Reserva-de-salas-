import streamlit as st

from utils.estilo import aplicar_estilo
from utils.session import autenticado, usuario_atual
from utils.ui import normalizar_perfil, registrar_paginas
from views.calendario_view import calendario_view
from views.componentes import barra_superior
from views.coordenador_view import coordenador_view
from views.espacos_view import espacos_view
from views.home_view import home_view
from views.login_view import login_view
from views.perfil_view import perfil_view
from views.reservas_view import reservas_view


st.set_page_config(
    page_title="UniReserve",
    page_icon=":material/menu_book:",
    layout="wide",
)
aplicar_estilo()

PODEM_RESERVAR = {"professor", "externo", "coordenador"}


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


def pagina_perfil():
    perfil_view(usuario_atual())


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
    pode_reservar = perfil in PODEM_RESERVAR

    inicio = st.Page(pagina_inicio, title="Início", icon=":material/home:", url_path="inicio", default=True)
    espacos = st.Page(
        pagina_espacos,
        title="Reservar sala" if pode_reservar else "Salas",
        icon=":material/calendar_today:",
        url_path="salas",
    )
    # Páginas fora do menu: abertas pelos botões "Ver agenda" e pelo avatar.
    calendario = st.Page(pagina_calendario, title="Agenda", icon=":material/calendar_month:",
                         url_path="agenda", visibility="visible" if not pode_reservar else "hidden")
    perfil_pagina = st.Page(pagina_perfil, title="Meu perfil", icon=":material/person:",
                            url_path="perfil", visibility="hidden")

    paginas = [inicio, espacos]
    disponiveis = {"inicio": inicio, "espacos": espacos, "calendario": calendario, "perfil": perfil_pagina}
    if pode_reservar:
        reservas = st.Page(pagina_reservas, title="Minhas reservas",
                           icon=":material/format_list_bulleted:", url_path="minhas-reservas")
        paginas.append(reservas)
        disponiveis["reservas"] = reservas
    if perfil == "coordenador":
        coordenacao = st.Page(pagina_coordenacao, title="Área do coordenador",
                              icon=":material/person:", url_path="coordenador")
        paginas.append(coordenacao)
        disponiveis["coordenacao"] = coordenacao
    paginas += [calendario, perfil_pagina]
    registrar_paginas(disponiveis)

    st.logo("assets/logo.svg", size="large", link=None)
    pagina = st.navigation(paginas)
    with st.sidebar:
        with st.container(key="link_config"):
            st.page_link(perfil_pagina, label="Configurações", icon=":material/settings:")
    barra_superior(usuario, perfil, perfil_pagina)
    pagina.run()


app()
