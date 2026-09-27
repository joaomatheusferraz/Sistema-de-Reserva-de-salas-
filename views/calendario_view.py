import streamlit as st

from controllers.reserva_controller import ReservaController


def calendario_view(usuario):
    st.title("Calendário")
    st.caption("As reservas pendentes e confirmadas bloqueiam o período.")
    reservas = ReservaController().listar_reservas_do_responsavel(usuario["id"])
    if isinstance(reservas, tuple):
        st.error(reservas[1])
        return
    if not reservas:
        st.info("Nenhuma reserva para exibir.")
        return
    st.dataframe(
        [
            {
                "Espaço": item.get("espaco_id"),
                "Início": item.get("inicio"),
                "Fim": item.get("fim"),
                "Status": item.get("status"),
            }
            for item in reservas
        ],
        use_container_width=True,
    )
