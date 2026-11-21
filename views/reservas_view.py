"""Minhas reservas: tabela com filtros, status e ações (protótipo do Figma)."""

from datetime import timedelta

import streamlit as st

from controllers.reserva_controller import ReservaController
from utils.ui import (
    agora,
    cabecalho,
    formatar_data,
    formatar_hora,
    normalizar_perfil,
    para_local,
    situacao_reserva,
)
from views.componentes import carregar_espacos, carregar_ocupacao, rotulos_unicos
from views.reserva_dialogos import dialogo_cancelar, dialogo_detalhes, dialogo_editar

POR_PAGINA = 10
PERIODOS = ["Últimos 30 dias", "Últimos 7 dias", "Próximas", "Todas"]
STATUS_FILTRO = ["Todos", "Confirmada", "Pendente", "Concluída", "Cancelada", "Recusada", "Expirada"]
COLUNAS = [1.1, 1.1, 2.4, 2.4, 1.2, 0.9]


def reservas_view(usuario):
    perfil = normalizar_perfil(usuario)
    cabecalho("Minhas reservas")

    if perfil not in {"professor", "externo", "coordenador"}:
        st.info("Alunos consultam salas e a agenda, mas não fazem reservas.", icon=":material/info:")
        return

    if mensagem := st.session_state.pop("reserva_mensagem", None):
        st.success(mensagem, icon=":material/check_circle:")

    try:
        reservas = ReservaController().listar_reservas_do_responsavel(usuario["id"])
    except Exception:
        reservas = (False, "Não foi possível carregar suas reservas. Tente novamente mais tarde.")
    if isinstance(reservas, tuple):
        st.error(reservas[1], icon=":material/error:")
        return

    espacos, _ = carregar_espacos(apenas_ativos=False)
    nomes = rotulos_unicos(espacos)
    reservaveis = [e for e in espacos if e.get("ativo", True)]
    if perfil == "externo":
        autorizados = set(usuario.get("espacos_autorizados_ids") or [])
        reservaveis = [e for e in reservaveis if e["id"] in autorizados]

    periodo, sala, status = _filtros(reservas, nomes)
    momento = agora()
    filtradas = [
        r for r in reservas
        if _no_periodo(r, periodo, momento)
        and (sala == "Todas" or r.get("espaco_id") == sala)
        and (status == "Todos" or situacao_reserva(r, momento)[0] == status)
    ]
    filtradas.sort(key=lambda r: r["inicio"], reverse=True)

    with st.container(key="card_tabela"):
        _cabecalho_tabela()
        if not filtradas:
            st.space("small")
            st.caption("Nenhuma reserva encontrada com esses filtros.", text_alignment="center")
            st.space("small")
        else:
            total_paginas = max(1, -(-len(filtradas) // POR_PAGINA))
            pagina = min(st.session_state.get("minhas_pagina", 1), total_paginas)
            inicio = (pagina - 1) * POR_PAGINA
            for reserva in filtradas[inicio:inicio + POR_PAGINA]:
                _linha(reserva, nomes, usuario, perfil, reservaveis, momento)
            st.space("medium")
            _paginacao(pagina, total_paginas)


def _filtros(reservas, nomes):
    salas = ["Todas"] + sorted(
        {r.get("espaco_id") for r in reservas if r.get("espaco_id")},
        key=lambda i: nomes.get(i, i).lower(),
    )
    with st.container(key="card_filtros"):
        with st.form("filtros_minhas", border=False):
            with st.container(horizontal=True, vertical_alignment="center", gap="medium"):
                st.markdown("Data:", width="content")
                periodo = st.selectbox("Data", PERIODOS, label_visibility="collapsed", width=190)
                st.markdown("Sala:", width="content")
                sala = st.selectbox(
                    "Sala", salas, format_func=lambda i: i if i == "Todas" else nomes.get(i, "Sala removida"),
                    label_visibility="collapsed", width=230,
                )
                st.markdown("Status:", width="content")
                status = st.selectbox("Status", STATUS_FILTRO, label_visibility="collapsed", width=160)
                st.space("stretch")
                filtrar = st.form_submit_button("Filtrar")
    if filtrar:
        st.session_state["minhas_pagina"] = 1
    return periodo, sala, status


def _no_periodo(reserva, periodo, momento):
    inicio = reserva.get("inicio")
    if not inicio:
        return periodo == "Todas"
    inicio = para_local(inicio)
    if periodo == "Últimos 30 dias":
        return momento - timedelta(days=30) <= inicio <= momento
    if periodo == "Últimos 7 dias":
        return momento - timedelta(days=7) <= inicio <= momento
    if periodo == "Próximas":
        return para_local(reserva["fim"]) >= momento
    return True


def _cabecalho_tabela():
    with st.container(key="cabecalho_tabela_minhas"):
        colunas = st.columns(COLUNAS, vertical_alignment="center")
        for coluna, titulo in zip(colunas, ["Data", "Horário", "Sala/Laboratório", "Motivo", "Status", "Ações"]):
            coluna.markdown(titulo, text_alignment="center" if titulo == "Ações" else "left")


def _linha(reserva, nomes, usuario, perfil, reservaveis, momento):
    rid = reserva["id"]
    nome_sala = nomes.get(reserva.get("espaco_id"), "Sala removida")
    rotulo, cor = situacao_reserva(reserva, momento)
    ativa = reserva.get("status") in {"pendente", "reservada"} and para_local(reserva["fim"]) >= momento

    with st.container(key=f"linha_{rid}"):
        data, horario, sala, motivo, status, acoes = st.columns(COLUNAS, vertical_alignment="center")
        data.markdown(formatar_data(reserva["inicio"]))
        horario.markdown(f"{formatar_hora(reserva['inicio'])} - {formatar_hora(reserva['fim'])}")
        sala.markdown(nome_sala)
        motivo.markdown(reserva.get("finalidade") or "—")
        with status:
            st.badge(rotulo, color=cor)
        with acoes:
            with st.container(horizontal=True, gap="small", horizontal_alignment="center"):
                if ativa:
                    editavel = reserva.get("status") == "pendente" or perfil == "coordenador"
                    if st.button(
                        "", icon=":material/edit:", key=f"tab_editar_{rid}",
                        disabled=not editavel,
                        help="Editar" if editavel else "Reservas aprovadas só podem ser alteradas pela coordenação",
                    ):
                        ocupacao, _ = carregar_ocupacao()
                        dialogo_editar(reserva, usuario, perfil, reservaveis, nomes, ocupacao)
                    if st.button("", icon=":material/cancel:", key=f"tab_cancelar_{rid}", help="Cancelar"):
                        dialogo_cancelar(reserva, usuario, perfil)
                elif st.button("", icon=":material/visibility:", key=f"tab_ver_{rid}", help="Ver detalhes"):
                    dialogo_detalhes(reserva, nome_sala)


def _ir_para_pagina(numero):
    st.session_state["minhas_pagina"] = numero


def _paginacao(pagina, total):
    with st.container(horizontal=True, horizontal_alignment="right", gap="xsmall"):
        botoes = [
            ("primeira", ":material/keyboard_double_arrow_left:", 1, pagina == 1),
            ("anterior", ":material/chevron_left:", pagina - 1, pagina == 1),
        ]
        for nome, icone, destino, desabilitado in botoes:
            st.button("", icon=icone, key=f"pagina_{nome}", disabled=desabilitado,
                      on_click=_ir_para_pagina, args=(destino,))
        janela = range(max(1, pagina - 2), min(total, pagina + 2) + 1)
        for numero in janela:
            st.button(
                str(numero), key=f"pagina_{numero}",
                type="primary" if numero == pagina else "secondary",
                on_click=_ir_para_pagina, args=(numero,),
            )
        for nome, icone, destino, desabilitado in [
            ("proxima", ":material/chevron_right:", pagina + 1, pagina == total),
            ("ultima", ":material/keyboard_double_arrow_right:", total, pagina == total),
        ]:
            st.button("", icon=icone, key=f"pagina_{nome}", disabled=desabilitado,
                      on_click=_ir_para_pagina, args=(destino,))
