import streamlit as st

from controllers.espaco_controller import EspacoController


def espacos_view():
    st.title("Espaços")
    try:
        espacos = EspacoController().listar_espacos()
    except Exception:
        st.error("Não foi possível carregar os espaços.")
        return

    if not espacos:
        st.info("Nenhum espaço ativo cadastrado.")
        return

    for espaco in espacos:
        with st.expander(f"{espaco.get('nome')} - {espaco.get('tipo')}"):
            st.write(f"Capacidade: {espaco.get('capacidade')}")
            st.write(f"Localização: {espaco.get('localizacao', {})}")
            st.write(", ".join(espaco.get("caracteristicas", [])) or "Sem características informadas.")
