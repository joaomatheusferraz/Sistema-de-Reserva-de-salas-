"""Diálogos de reserva usados pelos cards de sala e por "Minhas reservas"."""

from datetime import time, timedelta

import streamlit as st

from controllers.reserva_controller import ReservaController
from utils.ui import (
    agora,
    combinar_local,
    formatar_hora,
    formatar_periodo,
    para_local,
    reservas_do_dia,
    situacao_reserva,
    tipo_espaco,
)


def painel_do_dia(espaco, ocupacao, dia, ignorar_id=None):
    """Mostra os horários já ocupados da sala no dia escolhido."""
    rotulo_tipo, icone_tipo = tipo_espaco(espaco.get("tipo"))
    ocupados = [
        r for r in reservas_do_dia(espaco["id"], ocupacao, dia)
        if r.get("id") != ignorar_id
    ]
    with st.container(border=True):
        st.markdown(
            f"**{icone_tipo} {espaco.get('nome')}** · {rotulo_tipo} · "
            f":material/groups: {espaco.get('capacidade', '—')} lugares"
        )
        if ocupados:
            st.caption("Horários já ocupados neste dia:")
            with st.container(horizontal=True, gap="small"):
                for r in ocupados:
                    status = r.get("status")
                    icone, cor = {
                        "reservada": (":material/lock:", "red"),
                        "bloqueado": (":material/block:", "violet"),
                    }.get(status, (":material/schedule:", "orange"))
                    rotulo = f"{formatar_hora(r['inicio'])}–{formatar_hora(r['fim'])}"
                    if status == "bloqueado":
                        rotulo = f"Bloqueado {rotulo}"
                    st.badge(rotulo, icon=icone, color=cor)
        else:
            st.badge("Dia livre", icon=":material/check_circle:", color="green")


@st.dialog("Reservar sala", width="medium")
def dialogo_reservar(espaco, usuario, perfil, ocupacao):
    dia = st.date_input(
        "Dia",
        min_value=agora().date(),
        format="DD/MM/YYYY",
        key=f"dlg_reserva_dia_{espaco['id']}",
    )
    painel_do_dia(espaco, ocupacao, dia)
    with st.form(f"dlg_reserva_{espaco['id']}", border=False):
        with st.container(horizontal=True):
            inicio = st.time_input("Início", value=time(8, 0), step=timedelta(minutes=30))
            fim = st.time_input("Fim", value=time(9, 0), step=timedelta(minutes=30))
        finalidade = st.text_area(
            "Motivo",
            placeholder="Ex.: aula de Banco de Dados para a turma 3A",
        )
        enviar = st.form_submit_button(
            "Confirmar reserva" if perfil == "coordenador" else "Enviar solicitação",
            icon=":material/send:",
            type="primary",
            width="stretch",
        )
    if not enviar:
        return

    if fim <= inicio:
        st.error("O horário de término deve ser posterior ao horário de início.", icon=":material/error:")
        return
    if inicio < time(7, 0) or fim > time(23, 0):
        st.error("O horário de funcionamento do campus é das 07:00 às 23:00.", icon=":material/error:")
        return

    inicio_dt, fim_dt = combinar_local(dia, inicio), combinar_local(dia, fim)
    if inicio_dt < agora():
        st.error("Escolha um horário que ainda não passou.", icon=":material/error:")
        return
    sucesso, resultado = ReservaController().criar_reserva(
        espaco["id"], usuario["id"], inicio_dt, fim_dt, finalidade, perfil,
    )
    if not sucesso:
        st.error(resultado, icon=":material/error:")
        return
    periodo = f"{espaco.get('nome')}, {formatar_periodo(inicio_dt, fim_dt)}"
    st.session_state["salas_mensagem"] = (
        f"Reserva confirmada: {periodo}."
        if perfil == "coordenador" else
        f"Solicitação enviada: {periodo}. Aguarde a aprovação do coordenador."
    )
    st.rerun()


@st.dialog("Detalhes da reserva")
def dialogo_detalhes(reserva, nome_sala):
    rotulo, cor = situacao_reserva(reserva)
    st.markdown(f"**{nome_sala}**")
    st.badge(rotulo, color=cor)
    st.markdown(f":material/schedule: {formatar_periodo(reserva['inicio'], reserva['fim'])}")
    if reserva.get("finalidade"):
        st.caption(f"Motivo: {reserva['finalidade']}")
    if reserva.get("motivo_rejeicao"):
        st.warning(f"Motivo da recusa: {reserva['motivo_rejeicao']}", icon=":material/feedback:")


@st.dialog("Cancelar reserva?")
def dialogo_cancelar(reserva, usuario, perfil):
    st.write(formatar_periodo(reserva["inicio"], reserva["fim"]))
    st.caption("O horário volta a ficar livre para outras pessoas.")
    with st.container(horizontal=True):
        if st.button("Sim, cancelar", icon=":material/check:", type="primary"):
            ok, mensagem = ReservaController().cancelar_reserva(reserva["id"], usuario["id"], perfil)
            if ok:
                st.session_state["reserva_mensagem"] = mensagem
                st.rerun()
            st.error(mensagem)
        if st.button("Voltar", icon=":material/close:"):
            st.rerun()


@st.dialog("Editar reserva")
def dialogo_editar(reserva, usuario, perfil, espacos, rotulos, ocupacao):
    por_id = {e["id"]: e for e in espacos}
    if reserva["espaco_id"] not in por_id:
        st.warning("A sala desta reserva não está mais disponível para você.")
        return
    inicio_atual = para_local(reserva["inicio"])
    fim_atual = para_local(reserva["fim"])
    espaco_id = st.selectbox(
        "Sala",
        list(por_id),
        index=list(por_id).index(reserva["espaco_id"]),
        format_func=lambda i: rotulos.get(i, i),
    )
    dia = st.date_input(
        "Dia",
        value=max(inicio_atual.date(), agora().date()),
        min_value=agora().date(),
        format="DD/MM/YYYY",
    )
    painel_do_dia(por_id[espaco_id], ocupacao, dia, ignorar_id=reserva["id"])
    with st.container(horizontal=True):
        inicio = st.time_input("Início", value=inicio_atual.time().replace(tzinfo=None), step=timedelta(minutes=30))
        fim = st.time_input("Fim", value=fim_atual.time().replace(tzinfo=None), step=timedelta(minutes=30))
    finalidade = st.text_area("Motivo", value=reserva.get("finalidade", ""))
    if st.button("Salvar alterações", icon=":material/save:", type="primary"):
        if fim <= inicio:
            st.error("O horário de término deve ser posterior ao horário de início.", icon=":material/error:")
            return
        if inicio < time(7, 0) or fim > time(23, 0):
            st.error("O horário de funcionamento do campus é das 07:00 às 23:00.", icon=":material/error:")
            return
        inicio_dt, fim_dt = combinar_local(dia, inicio), combinar_local(dia, fim)
        if inicio_dt < agora():
            st.error("Escolha um horário que ainda não passou.", icon=":material/error:")
            return
        ok, mensagem = ReservaController().editar_reserva(
            reserva["id"],
            usuario["id"],
            perfil,
            {"espaco_id": espaco_id, "inicio": inicio_dt, "fim": fim_dt, "finalidade": finalidade},
        )
        if ok:
            st.session_state["reserva_mensagem"] = mensagem
            st.rerun()
        st.error(mensagem, icon=":material/error:")
