import streamlit as st

from controllers.usuario_controller import UsuarioController


def usuario_view():

    st.title("👤 Usuários")

    controller = UsuarioController()

    # ==========================================
    # CADASTRO
    # ==========================================

    st.subheader("Cadastrar usuário")

    nome = st.text_input(
        "Nome",
        key="nome_cadastro"
    )

    email = st.text_input(
        "E-mail",
        key="email_cadastro"
    )

    if st.button("Cadastrar"):

        sucesso, mensagem = controller.cadastrar_usuario(
            nome,
            email
        )

        if sucesso:

            st.success(mensagem)

            st.rerun()

        else:

            st.error(mensagem)

    st.divider()

    # ==========================================
    # LISTAGEM
    # ==========================================

    st.subheader("Usuários cadastrados")

    usuarios = controller.listar_usuarios()

    if not usuarios:

        st.info("Nenhum usuário cadastrado.")

        return

    # ==========================================
    # USUÁRIOS
    # ==========================================

    for usuario in usuarios:

        usuario_id = usuario["id"]

        with st.expander(
            f'{usuario["nome"]} — {usuario["email"]}'
        ):

            nome_editado = st.text_input(
                "Nome",
                value=usuario["nome"],
                key=f"nome_{usuario_id}"
            )

            email_editado = st.text_input(
                "E-mail",
                value=usuario["email"],
                key=f"email_{usuario_id}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Salvar alterações",
                    key=f"editar_{usuario_id}"
                ):

                    sucesso, mensagem = (
                        controller.atualizar_usuario(
                            usuario_id,
                            nome_editado,
                            email_editado
                        )
                    )

                    if sucesso:

                        st.success(mensagem)

                        st.rerun()

                    else:

                        st.error(mensagem)

            with col2:

                if st.button(
                    "Excluir",
                    key=f"excluir_{usuario_id}"
                ):

                    sucesso, mensagem = (
                        controller.excluir_usuario(
                            usuario_id
                        )
                    )

                    if sucesso:

                        st.success(mensagem)

                        st.rerun()

                    else:

                        st.error(mensagem)