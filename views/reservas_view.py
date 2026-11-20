from collections import Counter
from datetime import datetime, time

import streamlit as st

from controllers.reserva_controller import ReservaController
from controllers.espaco_controller import EspacoController
from utils.ui import localizacao_texto


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
        espacos = [item for item in espacos if item.get("ativo", True)]
        nomes = Counter(item["nome"] for item in espacos)
        opcoes = {}
        for item in espacos:
            nome = item["nome"]
            if nomes[nome] > 1:
                nome = f"{nome} · {localizacao_texto(item)}"
            opcoes[item["id"]] = nome
        rotulos = Counter(opcoes.values())
        for espaco_id, rotulo in opcoes.items():
            if rotulos[rotulo] > 1:
                opcoes[espaco_id] = f"{rotulo} ({espaco_id})"
        if not opcoes:
            st.warning(
                "Não há salas ativas disponíveis. Peça ao coordenador para "
                "cadastrar ou ativar uma sala em Espaços."
            )
        with st.form("solicitar_reserva", border=True):
            espaco_id = (
                st.selectbox("Espaço", list(opcoes), format_func=opcoes.__getitem__)
                if opcoes else None
            )
            data = st.date_input("Data")
            inicio = st.time_input("Horário inicial", value=time(8, 0))
            fim = st.time_input("Horário final", value=time(9, 0))
            finalidade = st.text_area("Finalidade")
            enviar = st.form_submit_button(
                "Enviar solicitação",
                type="primary",
                disabled=not opcoes,
            )

        if enviar and espaco_id:
            sucesso, resultado = controller.criar_reserva(
                espaco_id,
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
