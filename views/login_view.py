import streamlit as st

from controllers.auth_controller import AuthController


def login_view():
    st.title("UniReserve")
    st.subheader("Acesso ao sistema")
    with st.form("login_form"):
        ra = st.text_input("RA", key="login_ra")
        senha = st.text_input("Senha", type="password", key="login_senha")
        entrar = st.form_submit_button("Entrar", type="primary")

    if entrar:
        sucesso, mensagem = AuthController().login(ra, senha)
        if sucesso:
            st.rerun()
        st.error(mensagem)

    with st.expander("Ainda não tenho cadastro"):
        with st.form("cadastro_form"):
            nome = st.text_input("Nome completo", key="cadastro_nome")
            email = st.text_input("E-mail", key="cadastro_email")
            novo_ra = st.text_input("RA", key="cadastro_ra")
            perfil = st.selectbox(
                "Perfil",
                ["aluno", "professor", "externo"],
                format_func=lambda valor: {
                    "aluno": "Aluno",
                    "professor": "Professor",
                    "externo": "Usuário externo",
                }[valor],
                key="cadastro_perfil",
            )
            nova_senha = st.text_input("Senha", type="password", key="cadastro_senha")
            cadastrar = st.form_submit_button("Criar conta")
        if cadastrar:
            sucesso, mensagem = AuthController().registrar(
                nome, email, novo_ra, nova_senha, perfil
            )
            (st.success if sucesso else st.error)(mensagem)
