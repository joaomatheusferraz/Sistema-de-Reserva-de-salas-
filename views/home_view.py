"""Início: banner em carrossel e atalhos grandes (protótipo do Figma)."""

import streamlit as st

from controllers.notificacao_controller import NotificacaoController
from utils.ui import cabecalho, formatar_data, ir_para, pagina_disponivel

SLIDES = [
    (
        "Reserve salas em poucos cliques",
        "Encontre salas e laboratórios livres, filtre por capacidade e equipamentos e faça sua reserva na hora.",
        "calendar_month",
    ),
    (
        "Acompanhe suas reservas",
        "Veja o status de cada solicitação e gerencie seus horários em um só lugar.",
        "format_list_bulleted",
    ),
    (
        "Agenda sempre atualizada",
        "Consulte a ocupação de cada sala por dia, semana ou mês e descubra onde é cada aula.",
        "event_note",
    ),
]

ATALHOS = [
    # (página, rótulo, ícone, chave do botão)
    ("espacos", "Reservar sala", ":material/calendar_today:", "acao_salas"),
    ("reservas", "Minhas reservas", ":material/format_list_bulleted:", "acao_minhas"),
    ("coordenacao", "Área do coordenador", ":material/settings:", "acao_coordenador"),
]

ICONES_NOTIFICACAO = {
    "reserva_criada": (":material/send:", "blue"),
    "reserva_aprovada": (":material/check_circle:", "green"),
    "reserva_rejeitada": (":material/cancel:", "red"),
    "reserva_alterada": (":material/edit_calendar:", "orange"),
    "reserva_cancelada": (":material/event_busy:", "gray"),
}


def _mudar_slide(passo):
    st.session_state["banner_slide"] = (st.session_state.get("banner_slide", 1) + passo) % len(SLIDES)


def home_view(usuario):
    cabecalho("Início")
    _banner()
    st.space("medium")

    with st.container(horizontal_alignment="center"):
        with st.container(width=900, gap="medium"):
            atalhos = [a for a in ATALHOS if pagina_disponivel(a[0])]
            if not pagina_disponivel("reservas"):
                # Alunos não reservam: o atalho leva às salas e à agenda.
                atalhos[0] = ("espacos", "Salas", ":material/meeting_room:", "acao_salas")
                atalhos.append(("calendario", "Agenda", ":material/calendar_month:", "acao_agenda"))
            for pagina, rotulo, icone, chave in atalhos:
                if st.button(rotulo, icon=icone, key=chave, width="stretch"):
                    ir_para(pagina)

            _notificacoes(usuario)


def _banner():
    atual = st.session_state.setdefault("banner_slide", 1)
    titulo, texto, icone = SLIDES[atual]
    with st.container(horizontal_alignment="center"):
        with st.container(key="banner", width=1230):
            with st.container(horizontal=True, vertical_alignment="center"):
                with st.container(width="stretch", gap="small"):
                    st.markdown(f"## {titulo}")
                    st.markdown(texto, width=560)
                with st.container(key="banner_icone", horizontal_alignment="center",
                                  vertical_alignment="center", width=116, height=116, border=False):
                    st.html(f'<span class="ur-icone ur-icone-banner">{icone}</span>', width="content")
            st.space("medium")
            with st.container(key="banner_nav", horizontal=True, vertical_alignment="center",
                              gap="xsmall", width="content"):
                st.button("Anterior", icon=":material/chevron_left:", type="tertiary", key="banner_ant",
                          on_click=_mudar_slide, args=(-1,), help="Slide anterior")
                pontos = "".join(
                    f'<span class="{"ativo" if i == atual else ""}"></span>' for i in range(len(SLIDES))
                )
                st.html(f'<div class="ur-pontos">{pontos}</div>', width="content")
                st.button("Próximo", icon=":material/chevron_right:", type="tertiary", key="banner_prox",
                          on_click=_mudar_slide, args=(1,), help="Próximo slide")


def _notificacoes(usuario):
    """RF51: notificações de reserva na tela inicial."""
    controller = NotificacaoController()
    nao_lidas = controller.listar_do_usuario(usuario["id"], apenas_nao_lidas=True)
    if erro := st.session_state.pop("erro_notificacoes", None):
        st.warning(erro)
    if not nao_lidas:
        return
    with st.container(key="card_notificacoes"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown(f"**:material/notifications_active: Notificações** :red-badge[{len(nao_lidas)} nova(s)]")
            if st.button("Marcar todas como lidas", icon=":material/done_all:", key="notif_todas", type="tertiary"):
                resultados = [controller.marcar_como_lida(n["id"]) for n in nao_lidas]
                if not all(resultados):
                    st.session_state["erro_notificacoes"] = "Não foi possível marcar todas as notificações como lidas."
                st.rerun()
        for n in nao_lidas[:5]:
            icone, cor = ICONES_NOTIFICACAO.get(n.get("tipo"), (":material/info:", "gray"))
            with st.container(horizontal=True, vertical_alignment="center"):
                quando = formatar_data(n["created_at"]) if n.get("created_at") else ""
                st.markdown(f":{cor}[{icone}] {n.get('mensagem')}  \n:gray[{quando}]")
                if st.button("Lida", icon=":material/done:", key=f"notif_{n['id']}", help="Marcar como lida", type="tertiary"):
                    if controller.marcar_como_lida(n["id"]):
                        st.rerun()
                    st.warning("Não foi possível marcar a notificação como lida.")
