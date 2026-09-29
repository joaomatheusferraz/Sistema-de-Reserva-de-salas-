from datetime import datetime, time

import streamlit as st

from controllers.reserva_controller import ReservaController
from controllers.espaco_controller import EspacoController


def criar_controller_reservas():
    try:
        return ReservaController()
    except Exception:
        return None


def criar_controller_espacos():
    try:
        return EspacoController()
    except Exception:
        return None


def reservas_view(usuario):
    st.title("Reservas")

    nome = usuario.get("nome", "Carlos Silva")
    perfil = usuario.get("perfil", "Coordenador").title()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(nome)
    with col2:
        st.caption(f"Perfil: {perfil}")

    busca = st.text_input("Buscar sala, laboratório ou equipamento...", label_visibility="collapsed")
    filtro_capacidade = st.selectbox("Capacidade", [">20", ">50", ">100"], index=0)
    filtro_localizacao = st.selectbox("Localização", ["Bloco A", "Bloco B", "Bloco C"], index=0)
    filtro_equipamento = st.selectbox("Equipamentos", ["Projetor", "Wi‑Fi", "Lousa"], index=0)
    filtro_tipo = st.selectbox("Tipo", ["Sala de Aula", "Laboratório", "Auditório"], index=0)
    filtro_disponibilidade = st.date_input("Disponibilidade", value=datetime.today())

    salas = [
        {"nome": "Sala 201", "bloco": "Bloco A", "capacidade": 40, "status": "Disponível agora", "tags": ["Projetor", "Wi‑Fi", "Lousa"], "disponivel": True},
        {"nome": "Sala 202", "bloco": "Bloco A", "capacidade": 40, "status": "Disponível agora", "tags": ["Projetor", "Wi‑Fi", "Lousa"], "disponivel": True},
        {"nome": "Sala 203", "bloco": "Bloco A", "capacidade": 40, "status": "Ocupado até 10:30", "tags": ["Projetor", "Wi‑Fi", "Lousa"], "disponivel": False},
        {"nome": "Auditório", "bloco": "Bloco B", "capacidade": 120, "status": "Disponível agora", "tags": ["Sistema de som", "Projetor", "Wi‑Fi"], "disponivel": True},
        {"nome": "Sala 101", "bloco": "Bloco A", "capacidade": 40, "status": "Disponível agora", "tags": ["Projetor", "Wi‑Fi", "Lousa"], "disponivel": True},
        {"nome": "Lab. Informática", "bloco": "Bloco C", "capacidade": 40, "status": "Ocupado até 10:30", "tags": ["Projetor", "PC"], "disponivel": False},
        {"nome": "Sala 204", "bloco": "Bloco A", "capacidade": 40, "status": "Bloqueado", "tags": ["Projetor", "Wi‑Fi", "Lousa"], "disponivel": False},
        {"nome": "Sala 208", "bloco": "Bloco A", "capacidade": 40, "status": "Disponível agora", "tags": ["Projetor", "Wi‑Fi", "Lousa"], "disponivel": True},
    ]

    for i in range(0, len(salas), 4):
        cards = st.columns(4)
        for j, sala in enumerate(salas[i : i + 4]):
            with cards[j]:
                if sala["disponivel"]:
                    st.success(sala["status"])
                elif sala["status"] == "Bloqueado":
                    st.warning(sala["status"])
                else:
                    st.error(sala["status"])

                st.subheader(sala["nome"])
                st.caption(f"{sala['bloco']} · Capacidade: {sala['capacidade']} lugares")
                st.write("Equipamento")
                st.write(" • ".join(sala["tags"]))
                st.button("Reservar", key=f"reserva_{sala['nome']}_{i}_{j}", use_container_width=True, disabled=not sala["disponivel"])

    perfil = usuario.get("perfil", "aluno")
    controller = criar_controller_reservas()
    espaco_controller = criar_controller_espacos()

    if perfil in {"professor", "externo"}:
        st.subheader("Solicitar reserva")
        opcoes = {}

        if espaco_controller is not None:
            try:
                espacos = espaco_controller.listar_espacos()
                opcoes = {
                    item["nome"]: item["id"]
                    for item in espacos
                    if item.get("ativo", True)
                }
            except Exception:
                opcoes = {}

        if not opcoes:
            opcoes = {
                "Sala 201": "demo-201",
                "Sala 202": "demo-202",
                "Auditório": "demo-auditorio",
            }
            st.caption("Modo demonstração: sem Firebase configurado, a reserva fica visual apenas.")

        if not opcoes:
            st.warning("Não há espaços ativos disponíveis para reserva.")
        with st.form("solicitar_reserva", border=True):
            nome_espaco = st.selectbox("Espaço", list(opcoes)) if opcoes else None
            data = st.date_input("Data")
            inicio = st.time_input("Horário inicial", value=time(8, 0))
            fim = st.time_input("Horário final", value=time(9, 0))
            finalidade = st.text_area("Finalidade")
            enviar = st.form_submit_button(
                "Enviar solicitação",
                type="primary",
                disabled=not opcoes or controller is None,
            )

        if enviar and nome_espaco and controller is not None:
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
        elif enviar and controller is None:
            st.info("Modo de demonstração: a reserva visual foi aceita no front-end, mas o backend está desabilitado.")
    else:
        st.info("Este perfil não solicita reservas.")

    st.divider()
    st.subheader("Minhas solicitações")
    reservas = []
    if controller is not None:
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
        st.write(f"**{reserva.get('espaco_id')}**")
        st.write(f"{reserva.get('inicio')} até {reserva.get('fim')}")
        st.write(f"Status: {reserva.get('status')}")
