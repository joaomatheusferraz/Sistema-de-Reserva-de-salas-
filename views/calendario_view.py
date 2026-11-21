from datetime import datetime, time, timedelta

import streamlit as st

from controllers.usuario_controller import UsuarioController
from utils.ui import (
    FUSO_LOCAL,
    STATUS,
    agora,
    cabecalho,
    estado_vazio,
    formatar_data,
    formatar_hora,
    para_local,
)
from views.componentes import carregar_espacos, carregar_ocupacao, rotulos_unicos

# Janela usada para calcular os horários livres de uma sala (RN07).
ABERTURA = time(7, 0)
FECHAMENTO = time(23, 0)


def calendario_view(usuario):
    cabecalho(
        "Agenda de salas",
        "Descubra onde é cada aula: pesquise pelo professor, pela sala ou pela atividade.",
        ":material/calendar_month:",
    )
    ocupacao, erro_reservas = carregar_ocupacao()
    if erro_reservas:
        st.error(erro_reservas, icon=":material/error:")
        return
    # Inclui salas desativadas para que reservas antigas continuem com nome.
    espacos, erro = carregar_espacos(apenas_ativos=False)
    if erro:
        st.warning("Não foi possível carregar os nomes das salas.", icon=":material/warning:")
    nomes = rotulos_unicos(espacos)
    pessoas = {u["id"]: u.get("nome") or "—" for u in UsuarioController().listar_usuarios()}

    preselecao = st.session_state.pop("agenda_espaco_id", None)
    if preselecao in nomes:
        st.session_state["agenda_salas"] = [preselecao]
        st.session_state["agenda_periodo"] = "Dia"

    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="bottom"):
            periodo = st.segmented_control(
                "Visualizar",
                ["Dia", "Semana", "Mês"],
                default="Semana",
                key="agenda_periodo",
            ) or "Semana"
            referencia = st.date_input(
                "Data", value=agora().date(), format="DD/MM/YYYY", key="agenda_data"
            )
        with st.container(horizontal=True, vertical_alignment="bottom"):
            salas = st.multiselect(
                "Salas",
                list(nomes),
                format_func=lambda i: nomes.get(i, i),
                placeholder="Todas as salas",
                key="agenda_salas",
            )
            busca = st.text_input(
                "Buscar",
                placeholder="Professor, atividade ou sala",
                icon=":material/search:",
                key="agenda_busca",
            ).strip().lower()

    inicio_janela, fim_janela = _janela(periodo, referencia)
    st.caption(
        formatar_data(inicio_janela, com_dia_semana=True)
        + ("" if periodo == "Dia"
           else f" até {formatar_data(fim_janela - timedelta(seconds=1), com_dia_semana=True)}")
    )

    linhas = []
    for r in ocupacao:
        inicio, fim = para_local(r.get("inicio")), para_local(r.get("fim"))
        if not inicio or not fim or not (inicio < fim_janela and fim > inicio_janela):
            continue
        if salas and r.get("espaco_id") not in salas:
            continue
        sala = nomes.get(r.get("espaco_id"), "Sala removida")
        if r.get("bloqueio"):
            responsavel, atividade = "Coordenação", r.get("motivo") or "Bloqueio"
        else:
            responsavel = pessoas.get(r.get("responsavel_id"), "—")
            atividade = r.get("finalidade") or "—"
        if busca and busca not in f"{sala} {responsavel} {atividade}".lower():
            continue
        rotulo, _, _ = STATUS.get(r.get("status"), (r.get("status"), None, None))
        linhas.append(_linha(inicio, fim, sala, responsavel, atividade, rotulo))

    # Calendário da sala (RF15/RF44): um dia + uma sala mostra também as janelas livres.
    if periodo == "Dia" and len(salas) == 1 and not busca:
        linhas += _horarios_livres(linhas, referencia)

    if not linhas:
        mensagem = (
            "Nenhum horário encontrado com os filtros selecionados."
            if salas or busca else "Nenhum horário ocupado nesse período."
        )
        estado_vazio(
            mensagem,
            ":material/event_available:",
        )
        return

    linhas.sort(key=lambda linha: linha["_inicio"])
    ocupados = sum(1 for linha in linhas if linha["Situação"] != "Disponível")
    st.caption(f"{ocupados} horários ocupados")
    st.dataframe(
        [{k: v for k, v in linha.items() if not k.startswith("_")} for linha in linhas],
        hide_index=True,
    )


def _linha(inicio, fim, sala, responsavel, atividade, situacao):
    if inicio.date() != fim.date():
        horario = f"{formatar_data(inicio)} {formatar_hora(inicio)} → {formatar_data(fim)} {formatar_hora(fim)}"
    else:
        horario = f"{formatar_hora(inicio)}–{formatar_hora(fim)}"
    return {
        "_inicio": inicio,
        "_fim": fim,
        "Dia": formatar_data(inicio, com_dia_semana=True),
        "Horário": horario,
        "Sala": sala,
        "Responsável": responsavel,
        "Atividade": atividade,
        "Situação": situacao,
    }


def _janela(periodo, referencia):
    if periodo == "Dia":
        inicio, fim = referencia, referencia + timedelta(days=1)
    elif periodo == "Semana":
        inicio = referencia - timedelta(days=referencia.weekday())
        fim = inicio + timedelta(days=7)
    else:
        inicio = referencia.replace(day=1)
        fim = (inicio + timedelta(days=32)).replace(day=1)
    return (
        datetime.combine(inicio, time(0, 0), tzinfo=FUSO_LOCAL),
        datetime.combine(fim, time(0, 0), tzinfo=FUSO_LOCAL),
    )


def _horarios_livres(linhas, dia):
    cursor = datetime.combine(dia, ABERTURA, tzinfo=FUSO_LOCAL)
    fechamento = datetime.combine(dia, FECHAMENTO, tzinfo=FUSO_LOCAL)
    livres = []
    for linha in sorted(linhas, key=lambda item: item["_inicio"]):
        if linha["_inicio"] > cursor:
            livres.append((cursor, min(linha["_inicio"], fechamento)))
        cursor = max(cursor, linha["_fim"])
    if cursor < fechamento:
        livres.append((cursor, fechamento))
    return [
        _linha(inicio, fim, "", "", "", "Disponível")
        for inicio, fim in livres
        if inicio < fim
    ]
