import streamlit as st

from controllers.reserva_controller import ReservaController


def coordenador_view(usuario):
    if usuario.get("perfil") != "coordenador":
        st.error("Acesso restrito ao coordenador.")
        return

    st.title("Área do coordenador")
    st.subheader("Solicitações pendentes")
    controller = ReservaController()
    pendentes = controller.listar_pendentes(usuario.get("perfil"))
    if isinstance(pendentes, tuple):
        st.error(pendentes[1])
        return
    if not pendentes:
        st.info("Nenhuma solicitação pendente.")
        return

    for reserva in pendentes:
        with st.expander(f"Reserva {reserva['id']} - {reserva.get('espaco_id')}"):
            st.write(f"Responsável: {reserva.get('responsavel_id')}")
            st.write(f"Período: {reserva.get('inicio')} até {reserva.get('fim')}")
            st.write(f"Finalidade: {reserva.get('finalidade')}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Aprovar", key=f"aprovar_{reserva['id']}"):
                    ok, mensagem = controller.aprovar_reserva(
                        reserva["id"], usuario["id"], usuario["perfil"]
                    )
                    if ok:
                        st.success(mensagem)
                        st.rerun()
                    st.error(mensagem)
            with col2:
                motivo = st.text_input("Motivo da rejeição", key=f"motivo_{reserva['id']}")
                if st.button("Rejeitar", key=f"rejeitar_{reserva['id']}"):
                    ok, mensagem = controller.rejeitar_reserva(
                        reserva["id"], usuario["id"], usuario["perfil"], motivo
                    )
                    if ok:
                        st.success(mensagem)
                        st.rerun()
                    st.error(mensagem)
