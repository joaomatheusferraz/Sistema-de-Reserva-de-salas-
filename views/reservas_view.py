from datetime import datetime, time

import streamlit as st

from controllers.reserva_controller import ReservaController
from controllers.espaco_controller import EspacoController


def reservas_view(usuario):
    st.title("Reservas")
    perfil = usuario.get("perfil", "aluno")
    controller = ReservaController()

    if perfil in {"professor", "coordenador", "externo"}:
        st.subheader("Solicitar reserva")
        espacos = EspacoController().listar_espacos()
        opcoes = {item["nome"]: item["id"] for item in espacos}
        nome_espaco = st.selectbox("Espaço", list(opcoes)) if opcoes else None
        data = st.date_input("Data")
        inicio = st.time_input("Horário inicial", value=time(8, 0))
        fim = st.time_input("Horário final", value=time(9, 0))
        finalidade = st.text_area("Finalidade")

        if st.button("Enviar solicitação", type="primary") and nome_espaco:
            sucesso, resultado = controller.criar_reserva(
                opcoes[nome_espaco],
                usuario["id"],
                datetime.combine(data, inicio),
                datetime.combine(data, fim),
                finalidade,
                perfil,
            )
            if sucesso:
                st.success("Solicitação enviada com sucesso.")
                st.rerun()
            else:
                st.error(resultado)
    elif perfil == "aluno":
        st.info("Alunos podem consultar espaços, mas não solicitam reservas.")

    st.divider()
    st.subheader("Minhas reservas")
    try:
        reservas = controller.listar_reservas_do_responsavel(usuario["id"])
    except Exception:
        reservas = []
    if isinstance(reservas, tuple):
        st.error(reservas[1])
        return
    if not reservas:
        st.info("Nenhuma reserva encontrada.")
        return
    for reserva in reservas:
        st.write(
            f"{reserva.get('espaco_id')} | {reserva.get('inicio')} até "
            f"{reserva.get('fim')} | {reserva.get('status')}"
        )
