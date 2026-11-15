import streamlit as st

from controllers.auth_controller import AuthController
from utils.ui import PERFIS


def _formulario_login():
    with st.form("login_form", border=False):
        ra = st.text_input(
            "RA",
            key="login_ra",
            placeholder="Seu registro acadêmico",
            icon=":material/badge:",
        )
        senha = st.text_input(
            "Senha",
            type="password",
            key="login_senha",
            placeholder="••••••••",
            icon=":material/lock:",
        )
        entrar = st.form_submit_button(
            "Entrar",
            type="primary",
            icon=":material/login:",
            width="stretch",
        )

    if entrar:
        with st.spinner("Verificando credenciais..."):
            sucesso, mensagem = AuthController().login(ra, senha)
        if sucesso:
            st.rerun()
        st.error(mensagem, icon=":material/error:")


def _formulario_cadastro():
    with st.form("cadastro_form", border=False):
        nome = st.text_input(
            "Nome completo",
            key="cadastro_nome",
            icon=":material/person:",
        )
        email = st.text_input(
            "E-mail",
            key="cadastro_email",
            placeholder="nome@instituicao.edu.br",
            icon=":material/mail:",
        )
        with st.container(horizontal=True):
            novo_ra = st.text_input("RA", key="cadastro_ra", icon=":material/badge:")
            perfil = st.selectbox(
                "Perfil",
                ["aluno", "professor", "externo"],
                format_func=lambda valor: PERFIS[valor][0],
                key="cadastro_perfil",
            )
        nova_senha = st.text_input(
            "Senha",
            type="password",
            key="cadastro_senha",
            icon=":material/lock:",
        )
        cadastrar = st.form_submit_button(
            "Criar conta",
            type="primary",
            icon=":material/person_add:",
            width="stretch",
        )

    if cadastrar:
        with st.spinner("Criando sua conta..."):
            sucesso, mensagem = AuthController().registrar(
                nome, email, novo_ra, nova_senha, perfil
            )
        if sucesso:
            st.success(mensagem, icon=":material/check_circle:")
        else:
            st.error(mensagem, icon=":material/error:")


def login_view():
    _, centro, _ = st.columns([1, 1.15, 1])
    with centro:
        st.space("large")
        with st.container(horizontal_alignment="center", gap="xsmall"):
            st.markdown("## :primary[:material/meeting_room:]", text_alignment="center")
            st.title("UniReserve", anchor=False, text_alignment="center")
            st.caption(
                "Reserve salas e laboratórios da sua instituição em poucos cliques.",
                text_alignment="center",
            )

        with st.container(border=True):
            aba_entrar, aba_cadastro = st.tabs(
                [":material/login: Entrar", ":material/person_add: Criar conta"]
            )
            with aba_entrar:
                _formulario_login()
            with aba_cadastro:
                _formulario_cadastro()

        st.caption(
            ":material/info: Alunos consultam a agenda; professores e usuários "
            "externos solicitam reservas, aprovadas pela coordenação.",
            text_alignment="center",
        )
