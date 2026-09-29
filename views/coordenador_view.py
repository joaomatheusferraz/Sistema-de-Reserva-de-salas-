import streamlit as st

from controllers.reserva_controller import ReservaController
from controllers.espaco_controller import EspacoController
from controllers.usuario_controller import UsuarioController


def coordenador_view(usuario):
    if usuario.get("perfil") != "coordenador":
        st.error("Acesso restrito ao coordenador.")
        return

    st.title("Área do coordenador")
    st.subheader("Solicitações pendentes")
    controller = ReservaController()
    espacos = EspacoController().listar_espacos()
    usuarios = UsuarioController().listar_usuarios()
    nomes_espacos = {item["id"]: item.get("nome", item["id"]) for item in espacos}
    nomes_usuarios = {item["id"]: item.get("nome", item["id"]) for item in usuarios}
    pendentes = controller.listar_pendentes(usuario.get("perfil"))
    if isinstance(pendentes, tuple):
        st.error(pendentes[1])
        return
    if not pendentes:
        st.info("Nenhuma solicitação pendente.")
        return

    for reserva in pendentes:
        espaco_id = reserva.get("espaco_id")
        responsavel_id = reserva.get("responsavel_id")
        with st.expander(
            f"{nomes_espacos.get(espaco_id, espaco_id)} — {reserva.get('inicio')}"
        ):
            st.write(f"Responsável: {nomes_usuarios.get(responsavel_id, responsavel_id)}")
            st.write(f"Período: {reserva.get('inicio')} até {reserva.get('fim')}")
            st.write(f"Finalidade: {reserva.get('finalidade')}")
            with st.container(horizontal=True):
                if st.button("Aprovar", key=f"aprovar_{reserva['id']}"):
                    ok, mensagem = controller.aprovar_reserva(
                        reserva["id"], usuario["id"], usuario["perfil"]
                    )
                    if ok:
                        st.success(mensagem)
                        st.rerun()
                    st.error(mensagem)
            motivo = st.text_input("Motivo da rejeição", key=f"motivo_{reserva['id']}")
            with st.container(horizontal=True):
                if st.button("Rejeitar", key=f"rejeitar_{reserva['id']}"):
                    ok, mensagem = controller.rejeitar_reserva(
                        reserva["id"], usuario["id"], usuario["perfil"], motivo
                    )
                    if ok:
                        st.success(mensagem)
                        st.rerun()
                    st.error(mensagem)
