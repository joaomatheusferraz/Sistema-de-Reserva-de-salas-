import streamlit as st

from controllers.usuario_controller import UsuarioController


def usuario_view():

    st.title("Teste Firebase")

    controller = UsuarioController()

    nome = st.text_input("Nome")

    email = st.text_input("E-mail")

    if st.button("Cadastrar"):

        sucesso, mensagem = controller.cadastrar_usuario(
            nome,
            email
        )

        if sucesso:
            st.success(mensagem)

        else:
            st.error(mensagem)