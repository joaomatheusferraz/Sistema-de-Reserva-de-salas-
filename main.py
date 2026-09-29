import streamlit as st

from controllers.auth_controller import AuthController
from utils.session import autenticado, usuario_atual
from views.calendario_view import calendario_view
from views.coordenador_view import coordenador_view
from views.espacos_view import espacos_view
from views.home_view import home_view
from views.login_view import login_view
from views.reservas_view import reservas_view


st.set_page_config(page_title="UniReserve", layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #4c2b74 0%, #43256d 100%);
            box-shadow: inset -1px 0 0 rgba(255,255,255,0.08);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 0.75rem;
            padding-bottom: 0.75rem;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: transparent;
            border: none;
            color: white;
            text-align: left;
            font-size: 1rem;
            font-weight: 500;
            padding: 0.7rem 0.9rem;
            border-radius: 10px;
            margin-bottom: 0.15rem;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.08);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def app():
    if not autenticado():
        st.session_state["usuario_autenticado"] = {
            "nome": "Carlos Silva",
            "perfil": "coordenador",
            "email": "carlos@unisapiens.edu.br",
        }
        st.session_state["pagina_atual"] = "inicio"

    usuario = usuario_atual()
    st.sidebar.markdown(
        """
        <div style='display:flex; align-items:center; gap:10px; padding: 0.25rem 0.4rem 1rem 0.4rem; color:white;'>
            <div style='width: 22px; height: 22px; border-radius: 7px; background: #f9c74f; display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.08);'>
                <svg width='14' height='14' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'>
                    <path d='M4 18.5V9.5L12 4L20 9.5V18.5H4Z' stroke='#43256d' stroke-width='1.8' stroke-linejoin='round'/>
                    <path d='M9 18.5V12.5H15V18.5' stroke='#43256d' stroke-width='1.8' stroke-linejoin='round'/>
                </svg>
            </div>
            <div style='font-size: 1.15rem; font-weight:700;'>UniReserve</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu = [
        ("Início", "inicio"),
        ("Reservar Sala", "reservar"),
        ("Minhas Reservas", "minhas"),
        ("Área do Coordenador", "coordenador"),
    ]

    for label, key in menu:
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state["pagina_atual"] = key
            st.rerun()

    if st.sidebar.button("Configurações", key="configuracoes", use_container_width=True):
        st.session_state["pagina_atual"] = "configuracoes"
        st.rerun()

    if st.sidebar.button("Sair", key="sair", use_container_width=True):
        AuthController.logout()
        st.session_state["pagina_atual"] = "inicio"
        st.rerun()

    if st.session_state.get("pagina_atual") == "inicio":
        home_view(usuario)
    elif st.session_state.get("pagina_atual") == "reservar":
        reservas_view(usuario)
    elif st.session_state.get("pagina_atual") == "minhas":
        reservas_view(usuario)
    elif st.session_state.get("pagina_atual") == "coordenador":
        coordenador_view(usuario)
    else:
        home_view(usuario)


app()
