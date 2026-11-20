import streamlit as st

from controllers.reserva_controller import ReservaController
from utils.ui import (
    agora,
    estado_vazio,
    formatar_data,
    formatar_periodo,
    ir_para,
    normalizar_perfil,
    pagina_disponivel,
    para_local,
    situacao_sala,
    status_badge,
)
from views.componentes import carregar_espacos, carregar_ocupacao, grade_salas


ACOES = [
    # (página, rótulo, ícone, destaque)
    ("reservas", "Reservar uma sala", ":material/add_circle:", True),
    ("coordenacao", "Analisar solicitações", ":material/fact_check:", True),
    ("espacos", "Ver salas", ":material/meeting_room:", False),
    ("calendario", "Agenda", ":material/calendar_month:", False),
]


def home_view(usuario):
    perfil = normalizar_perfil(usuario)
    primeiro_nome = (usuario.get("nome") or "usuário").split()[0]
    hoje = agora()

    st.title(f"Olá, {primeiro_nome}", icon=":material/waving_hand:", anchor=False)
    st.caption(f"{formatar_data(hoje, com_dia_semana=True)} · {hoje:%H:%M}")

    # Ações rápidas: só aparecem as páginas liberadas para o perfil.
    with st.container(horizontal=True, gap="small"):
        for pagina, rotulo, icone, destaque in ACOES:
            if pagina_disponivel(pagina):
                if st.button(
                    rotulo,
                    icon=icone,
                    type="primary" if destaque else "secondary",
                    key=f"acao_{pagina}",
                ):
                    ir_para(pagina)

    espacos, erro_espacos = carregar_espacos()
    reservas, erro_reservas = carregar_ocupacao()
    if erro_espacos or erro_reservas:
        st.error(erro_espacos or erro_reservas, icon=":material/error:")

    livres = [
        e for e in espacos
        if situacao_sala(e["id"], reservas, hoje)[0] == "Livre agora"
    ]
    hoje_reservas = [
        r for r in reservas
        if r.get("inicio") and para_local(r["inicio"]).date() == hoje.date()
    ]

    with st.container(horizontal=True):
        st.metric("Salas ativas", len(espacos), border=True)
        st.metric("Livres agora", len(livres), border=True)
        st.metric("Reservas hoje", len(hoje_reservas), border=True)
        _metrica_do_perfil(usuario, perfil, reservas)

    st.subheader("Salas disponíveis", anchor=False)
    if not espacos:
        estado_vazio(
            "Nenhuma sala cadastrada ainda."
            + (" Cadastre a primeira em Salas e espaços." if perfil == "coordenador" else ""),
            icone=":material/meeting_room:",
        )
    else:
        filtro = st.segmented_control(
            "Mostrar",
            ["Livres agora", "Todas"],
            default="Livres agora",
            key="home_filtro_salas",
            label_visibility="collapsed",
        )
        lista = livres if filtro == "Livres agora" else espacos
        if lista:
            grade_salas(lista, reservas, "home", perfil in {"professor", "externo"})
        else:
            estado_vazio("Todas as salas estão ocupadas neste momento.", ":material/event_busy:")

    if perfil in {"professor", "externo"}:
        _proximas_reservas(usuario, espacos)


def _metrica_do_perfil(usuario, perfil, reservas):
    if perfil == "coordenador":
        pendentes = sum(1 for r in reservas if r.get("status") == "pendente")
        st.metric("Aguardando análise", pendentes, border=True)
    elif perfil in {"professor", "externo"}:
        minhas = [r for r in reservas if r.get("responsavel_id") == usuario.get("id")]
        st.metric("Minhas reservas ativas", len(minhas), border=True)


def _proximas_reservas(usuario, espacos):
    st.subheader("Minhas próximas reservas", anchor=False)
    reservas = ReservaController().listar_reservas_do_responsavel(usuario["id"])
    if isinstance(reservas, tuple):
        st.error(reservas[1])
        return
    momento = agora()
    proximas = sorted(
        (
            r for r in reservas
            if r.get("status") in {"pendente", "reservada"}
            and r.get("fim") and para_local(r["fim"]) >= momento
        ),
        key=lambda r: r["inicio"],
    )[:3]
    if not proximas:
        estado_vazio("Você não tem reservas futuras.", ":material/event_available:")
        return
    nomes = {e["id"]: e.get("nome", e["id"]) for e in espacos}
    for reserva in proximas:
        with st.container(border=True, horizontal=True, vertical_alignment="center"):
            st.markdown(
                f"**{nomes.get(reserva['espaco_id'], 'Sala removida')}**  \n"
                f":material/schedule: {formatar_periodo(reserva['inicio'], reserva['fim'])}"
            )
            status_badge(reserva.get("status"))
