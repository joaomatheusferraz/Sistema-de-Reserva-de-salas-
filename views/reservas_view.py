from datetime import time, timedelta

import streamlit as st

from controllers.reserva_controller import ReservaController
from utils.ui import (
    agora,
    cabecalho,
    combinar_local,
    estado_vazio,
    formatar_hora,
    formatar_periodo,
    normalizar_perfil,
    para_local,
    reservas_do_dia,
    status_badge,
    tipo_espaco,
)
from views.componentes import carregar_espacos, carregar_ocupacao, rotulos_unicos


def reservas_view(usuario):
    perfil = normalizar_perfil(usuario)
    cabecalho(
        "Reservar sala",
        "Escolha a sala e o dia, veja os horários livres e envie a solicitação para o coordenador.",
        ":material/event_available:",
    )

    if perfil not in {"professor", "externo"}:
        st.info(
            "Somente professores e usuários externos solicitam reservas. "
            "Alunos consultam a agenda; o coordenador aprova as solicitações.",
            icon=":material/info:",
        )
        return

    if mensagem := st.session_state.pop("reserva_mensagem", None):
        st.success(mensagem, icon=":material/check_circle:")

    controller = ReservaController()
    espacos, erro = carregar_espacos()
    if erro:
        st.error(erro, icon=":material/error:")
    ocupacao, erro = carregar_ocupacao()
    if erro:
        st.error(erro, icon=":material/error:")

    nova, minhas = st.tabs([":material/add_circle: Nova reserva", ":material/list_alt: Minhas solicitações"])
    with nova:
        _formulario(usuario, perfil, espacos, ocupacao, controller)
    with minhas:
        _minhas_solicitacoes(usuario, perfil, espacos, controller)


def _formulario(usuario, perfil, espacos, ocupacao, controller):
    if not espacos:
        estado_vazio(
            "Não há salas ativas. Peça ao coordenador para cadastrar uma sala.",
            ":material/meeting_room:",
        )
        return

    por_id = {e["id"]: e for e in espacos}
    rotulos = rotulos_unicos(espacos)
    preselecao = st.session_state.pop("reserva_espaco_id", None)
    if preselecao in por_id:
        st.session_state["reserva_sala"] = preselecao

    with st.container(horizontal=True):
        espaco_id = st.selectbox(
            "Sala",
            list(por_id),
            format_func=lambda i: f"{rotulos[i]} · {por_id[i].get('capacidade')} lugares",
            key="reserva_sala",
        )
        dia = st.date_input(
            "Dia",
            min_value=agora().date(),
            format="DD/MM/YYYY",
            key="reserva_dia",
        )

    espaco = por_id[espaco_id]
    rotulo_tipo, icone_tipo = tipo_espaco(espaco.get("tipo"))
    ocupados = reservas_do_dia(espaco_id, ocupacao, dia)

    with st.container(border=True):
        st.markdown(f"**{icone_tipo} {espaco.get('nome')}** · {rotulo_tipo}")
        if ocupados:
            st.caption("Horários já ocupados neste dia:")
            with st.container(horizontal=True, gap="small"):
                for r in ocupados:
                    confirmada = r.get("status") == "reservada"
                    st.badge(
                        f"{formatar_hora(r['inicio'])}–{formatar_hora(r['fim'])}",
                        icon=":material/lock:" if confirmada else ":material/schedule:",
                        color="red" if confirmada else "orange",
                    )
        else:
            st.badge("Dia livre", icon=":material/check_circle:", color="green")

    with st.form("solicitar_reserva", border=True):
        with st.container(horizontal=True):
            inicio = st.time_input("Início", value=time(8, 0), step=timedelta(minutes=30))
            fim = st.time_input("Fim", value=time(9, 0), step=timedelta(minutes=30))
        finalidade = st.text_area(
            "Finalidade",
            placeholder="Ex.: aula de Banco de Dados para a turma 3A",
        )
        enviar = st.form_submit_button(
            "Enviar solicitação",
            icon=":material/send:",
            type="primary",
            width="stretch",
        )

    if not enviar:
        return

    inicio_dt = combinar_local(dia, inicio)
    fim_dt = combinar_local(dia, fim)
    if inicio_dt < agora():
        st.error("Escolha um horário que ainda não passou.", icon=":material/error:")
        return

    sucesso, resultado = controller.criar_reserva(
        espaco_id,
        usuario["id"],
        inicio_dt,
        fim_dt,
        finalidade,
        perfil,
    )
    if sucesso:
        st.session_state["reserva_mensagem"] = (
            f"Solicitação enviada: {espaco.get('nome')}, "
            f"{formatar_periodo(inicio_dt, fim_dt)}. Aguarde a aprovação do coordenador."
        )
        st.rerun()
    st.error(resultado, icon=":material/error:")


def _minhas_solicitacoes(usuario, perfil, espacos, controller):
    try:
        reservas = controller.listar_reservas_do_responsavel(usuario["id"])
    except Exception:
        st.error("Não foi possível carregar suas solicitações. Tente novamente mais tarde.", icon=":material/error:")
        return
    if isinstance(reservas, tuple):
        st.error(reservas[1])
        return
    if not reservas:
        estado_vazio("Você ainda não fez nenhuma solicitação.", ":material/inbox:")
        return

    momento = agora()
    filtro = st.segmented_control(
        "Filtrar",
        ["Próximas", "Histórico"],
        default="Próximas",
        key="reservas_filtro",
        label_visibility="collapsed",
    )

    def ativa(r):
        return r.get("status") in {"pendente", "reservada"} and para_local(r["fim"]) >= momento

    lista = [r for r in reservas if ativa(r) == (filtro != "Histórico")]
    lista.sort(key=lambda r: r["inicio"], reverse=filtro == "Histórico")
    if not lista:
        estado_vazio("Nada por aqui.", ":material/inbox:")
        return

    nomes = rotulos_unicos(espacos)
    for reserva in lista:
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"**:material/meeting_room: {nomes.get(reserva['espaco_id'], 'Sala removida')}**")
                status_badge(reserva.get("status"))
            st.markdown(f":material/schedule: {formatar_periodo(reserva['inicio'], reserva['fim'])}")
            if reserva.get("finalidade"):
                st.caption(reserva["finalidade"])
            if reserva.get("motivo_rejeicao"):
                st.warning(f"Motivo da rejeição: {reserva['motivo_rejeicao']}", icon=":material/feedback:")
            if ativa(reserva):
                if st.button(
                    "Cancelar reserva",
                    icon=":material/event_busy:",
                    key=f"cancelar_{reserva['id']}",
                ):
                    _confirmar_cancelamento(reserva, usuario, perfil, controller)


@st.dialog("Cancelar reserva?")
def _confirmar_cancelamento(reserva, usuario, perfil, controller):
    st.write(f"{formatar_periodo(reserva['inicio'], reserva['fim'])}")
    st.caption("O horário volta a ficar livre para outras pessoas.")
    with st.container(horizontal=True):
        if st.button("Sim, cancelar", icon=":material/check:", type="primary"):
            ok, mensagem = controller.cancelar_reserva(reserva["id"], usuario["id"], perfil)
            if ok:
                st.session_state["reserva_mensagem"] = mensagem
                st.rerun()
            st.error(mensagem)
        if st.button("Voltar", icon=":material/close:"):
            st.rerun()
