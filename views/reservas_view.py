from datetime import datetime, time

import streamlit as st

from controllers.reserva_controller import ReservaController
from controllers.espaco_controller import EspacoController


def reservas_view(usuario):
    st.title("Reservas")
    perfil = str(usuario.get("perfil", "aluno")).strip().lower()
    controller = ReservaController()

    if perfil in {"professor", "externo"}:
        st.subheader("Solicitar reserva")
        try:
            espacos = EspacoController().listar_espacos()
        except Exception as erro:
            st.error(f"Não foi possível carregar as salas do banco: {erro}")
            espacos = []
        opcoes = {
            item["nome"]: item["id"]
            for item in espacos
            if item.get("ativo", True)
        }
        if not opcoes:
            st.warning(
                "Não há salas ativas disponíveis. Peça ao coordenador para "
                "cadastrar ou ativar uma sala em Espaços."
            )
        with st.form("solicitar_reserva", border=True):
            nome_espaco = st.selectbox("Espaço", list(opcoes)) if opcoes else None
            data = st.date_input("Data")
            inicio = st.time_input("Horário inicial", value=time(8, 0))
            fim = st.time_input("Horário final", value=time(9, 0))
            finalidade = st.text_area("Finalidade")
            enviar = st.form_submit_button(
                "Enviar solicitação",
                type="primary",
                disabled=not opcoes,
            )

        if enviar and nome_espaco:
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
        st.info(
            "Sua conta é de aluno. Alunos podem consultar a agenda, mas "
            "somente professores e usuários externos solicitam reservas."
        )
    elif perfil == "coordenador":
        st.info(
            "Sua conta é de coordenador. O coordenador aprova ou rejeita "
            "solicitações; a reserva é feita por professor ou usuário externo."
        )
    else:
        st.warning(
            f"O perfil '{perfil}' não está configurado para solicitar reservas. "
            "Use aluno, professor, externo ou coordenador."
        )

    st.divider()
    st.subheader("Minhas solicitações")
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
