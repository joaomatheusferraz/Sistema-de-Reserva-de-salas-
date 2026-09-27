import streamlit as st


def home_view(usuario):
    st.title("UniReserve")
    st.write(f"Olá, {usuario.get('nome', 'usuário')}.")
    st.caption(f"Perfil: {usuario.get('perfil', 'não informado')}")
    st.info("Use o menu lateral para consultar espaços e acompanhar reservas.")
