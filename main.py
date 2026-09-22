import streamlit as st
from login import login


def main():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    if not st.session_state["logado"]:
        login()
    else:
        st.title("Sistema de Reserva de Salas")
        st.write("Bem-vindo ao sistema!")


if __name__ == "__main__":
    main()
