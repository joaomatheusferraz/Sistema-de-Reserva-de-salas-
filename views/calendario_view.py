import streamlit as st

from controllers.reserva_controller import ReservaController
from controllers.espaco_controller import EspacoController


def calendario_view(usuario):
    st.title("Agenda de salas")
    st.caption("Horários pendentes e confirmados ficam indisponíveis para novas solicitações.")
    reservas = ReservaController().listar_calendario()
    if isinstance(reservas, tuple):
        st.error(reservas[1])
        return
    if not reservas:
        st.info("Nenhum horário ocupado.")
        return
    espacos = EspacoController().listar_espacos()
    nomes = {item["id"]: item.get("nome", item["id"]) for item in espacos}
    st.dataframe(
        [
            {
                "Espaço": nomes.get(item.get("espaco_id"), item.get("espaco_id")),
                "Início": item.get("inicio"),
                "Fim": item.get("fim"),
                "Status": item.get("status"),
            }
            for item in reservas
        ],
        hide_index=True,
    )
