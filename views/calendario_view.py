from datetime import timedelta

import streamlit as st

from utils.ui import (
    STATUS,
    agora,
    cabecalho,
    estado_vazio,
    formatar_data,
    formatar_hora,
    para_local,
)
from views.componentes import carregar_espacos, carregar_ocupacao, rotulos_unicos


def calendario_view(usuario):
    cabecalho(
        "Agenda de salas",
        "Horários pendentes e confirmados ficam indisponíveis para novas solicitações.",
        ":material/calendar_month:",
    )
    reservas, erro_reservas = carregar_ocupacao()
    if erro_reservas:
        st.error(erro_reservas, icon=":material/error:")
        return
    # Inclui salas desativadas para que reservas antigas continuem com nome.
    espacos, erro = carregar_espacos(apenas_ativos=False)
    if erro:
        st.warning("Não foi possível carregar os nomes das salas.", icon=":material/warning:")

    nomes = rotulos_unicos(espacos)
    preselecao = st.session_state.pop("agenda_espaco_id", None)
    if preselecao in nomes:
        st.session_state["agenda_salas"] = [preselecao]

    hoje = agora().date()
    with st.container(horizontal=True, vertical_alignment="bottom"):
        salas = st.multiselect(
            "Salas",
            list(nomes),
            format_func=lambda i: nomes.get(i, i),
            placeholder="Todas as salas",
            key="agenda_salas",
        )
        periodo = st.segmented_control(
            "Período",
            ["Hoje", "Próximos 7 dias", "Próximos 30 dias"],
            default="Próximos 7 dias",
            key="agenda_periodo",
        ) or "Próximos 7 dias"

    dias = {"Hoje": 0, "Próximos 7 dias": 7, "Próximos 30 dias": 30}[periodo]
    limite = hoje + timedelta(days=dias)

    linhas = []
    for r in reservas:
        inicio = para_local(r.get("inicio"))
        if not inicio or not (hoje <= inicio.date() <= limite):
            continue
        if salas and r.get("espaco_id") not in salas:
            continue
        rotulo, _, _ = STATUS.get(r.get("status"), (r.get("status"), None, None))
        linhas.append({
            "Dia": formatar_data(r["inicio"], com_dia_semana=True),
            "Horário": f"{formatar_hora(r['inicio'])}–{formatar_hora(r['fim'])}",
            "Sala": nomes.get(r.get("espaco_id"), "Sala removida"),
            "Situação": rotulo,
        })

    if not linhas:
        estado_vazio("Nenhum horário ocupado nesse período. Todas as salas estão livres.", ":material/event_available:")
        return

    st.caption(f"{len(linhas)} horários ocupados")
    st.dataframe(linhas, hide_index=True)
