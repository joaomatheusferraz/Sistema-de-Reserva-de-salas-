import streamlit as st

from controllers.auth_controller import AuthController


def login_view():
    st.title("UniReserve")
    st.subheader("Acesso ao sistema")
    ra = st.text_input("RA")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", type="primary"):
        sucesso, mensagem = AuthController().login(ra, senha)
        if sucesso:
            st.rerun()
        st.error(mensagem)
