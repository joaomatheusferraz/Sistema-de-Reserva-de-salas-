import streamlit as st


def login():
    st.title("Login")

    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        enviado = st.form_submit_button("Entrar")

    if enviado:
        if usuario == "admin" and senha == "1234":
            st.session_state["logado"] = True
            st.success("Login realizado com sucesso!")
            return True

        st.error("Usuário ou senha inválidos.")
        return False

    return False
