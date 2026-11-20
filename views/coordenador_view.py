from datetime import time, timedelta

import streamlit as st

from controllers.bloqueio_controller import BloqueioController
from controllers.equipamento_controller import EquipamentoController
from controllers.reserva_controller import ReservaController
from controllers.usuario_controller import UsuarioController
from utils.ui import (
    PERFIS,
    STATUS,
    agora,
    cabecalho,
    combinar_local,
    estado_vazio,
    formatar_data,
    formatar_periodo,
    normalizar_perfil,
    para_local,
    perfil_badge,
    status_badge,
)
from views.componentes import carregar_espacos, rotulos_unicos

ACOES_HISTORICO = {
    "criacao": ("Criada", ":material/add_circle:"),
    "alteracao": ("Alterada", ":material/edit:"),
    "aprovacao": ("Aprovada", ":material/check_circle:"),
    "rejeicao": ("Rejeitada", ":material/cancel:"),
    "cancelamento": ("Cancelada", ":material/event_busy:"),
}


def coordenador_view(usuario):
    perfil = normalizar_perfil(usuario)
    if perfil != "coordenador":
        st.error("Acesso restrito ao coordenador.", icon=":material/lock:")
        return

    cabecalho(
        "Coordenação",
        "Analise solicitações, acompanhe todas as reservas e administre espaços, equipamentos e usuários.",
        ":material/fact_check:",
    )
    if mensagem := st.session_state.pop("coord_mensagem", None):
        st.success(mensagem, icon=":material/check_circle:")

    reservas_ctrl = ReservaController()
    usuarios_ctrl = UsuarioController()
    espacos, _ = carregar_espacos(apenas_ativos=False)
    usuarios = usuarios_ctrl.listar_usuarios()
    pendentes = reservas_ctrl.listar_pendentes(perfil)
    if isinstance(pendentes, tuple):
        st.error(pendentes[1])
        pendentes = []

    ctx = {
        "usuario": usuario,
        "perfil": perfil,
        "espacos": espacos,
        "nomes_espacos": rotulos_unicos(espacos),
        "nomes_usuarios": {u["id"]: u.get("nome") or "Sem nome" for u in usuarios},
        "reservas": reservas_ctrl,
    }

    abas = st.tabs([
        f":material/pending_actions: Solicitações ({len(pendentes)})",
        ":material/list_alt: Todas as reservas",
        ":material/block: Bloqueios",
        ":material/devices: Equipamentos",
        f":material/group: Usuários ({len(usuarios)})",
    ])
    with abas[0]:
        _solicitacoes(ctx, pendentes)
    with abas[1]:
        _todas_reservas(ctx)
    with abas[2]:
        _bloqueios(ctx)
    with abas[3]:
        _equipamentos()
    with abas[4]:
        _usuarios(ctx, usuarios, usuarios_ctrl)


def _concluir(ok, mensagem):
    if ok:
        st.session_state["coord_mensagem"] = mensagem
        st.rerun()
    st.error(mensagem)


# ---------------------------------------------------------------------------
# Solicitações pendentes

def _solicitacoes(ctx, pendentes):
    if not pendentes:
        estado_vazio("Nenhuma solicitação pendente. Tudo em dia!", ":material/task_alt:")
        return
    for reserva in sorted(pendentes, key=lambda r: r["inicio"]):
        rid = reserva["id"]
        with st.container(border=True):
            _resumo_reserva(ctx, reserva)
            with st.container(horizontal=True, gap="small"):
                if st.button("Aprovar", icon=":material/check_circle:", type="primary", key=f"aprovar_{rid}"):
                    _concluir(*ctx["reservas"].aprovar_reserva(rid, ctx["usuario"]["id"], ctx["perfil"]))
                if st.button("Rejeitar", icon=":material/cancel:", key=f"rejeitar_{rid}"):
                    _rejeitar(ctx, rid)


def _resumo_reserva(ctx, reserva):
    st.markdown(
        f"**:material/meeting_room: {ctx['nomes_espacos'].get(reserva.get('espaco_id'), 'Sala removida')}**  \n"
        f":material/schedule: {formatar_periodo(reserva['inicio'], reserva['fim'])}  \n"
        f":material/person: {ctx['nomes_usuarios'].get(reserva.get('responsavel_id'), 'Usuário removido')}"
    )
    if reserva.get("finalidade"):
        st.caption(f"Finalidade: {reserva['finalidade']}")


@st.dialog("Rejeitar solicitação")
def _rejeitar(ctx, reserva_id):
    motivo = st.text_area("Motivo da rejeição", placeholder="Ex.: sala reservada para evento da coordenação")
    if st.button("Confirmar rejeição", icon=":material/cancel:", type="primary"):
        _concluir(*ctx["reservas"].rejeitar_reserva(reserva_id, ctx["usuario"]["id"], ctx["perfil"], motivo))


# ---------------------------------------------------------------------------
# Todas as reservas (RF37, RF38) + histórico (seção 20)

def _todas_reservas(ctx):
    reservas = ctx["reservas"].listar_todas(ctx["perfil"])
    if isinstance(reservas, tuple):
        st.error(reservas[1])
        return
    if not reservas:
        estado_vazio("Nenhuma reserva registrada ainda.", ":material/inbox:")
        return

    with st.container(horizontal=True, vertical_alignment="bottom"):
        busca = st.text_input(
            "Pesquisar", placeholder="Usuário, sala ou finalidade",
            icon=":material/search:", key="todas_busca",
        ).strip().lower()
        status = st.multiselect(
            "Situação", [s for s in STATUS if s != "bloqueado"],
            format_func=lambda s: STATUS[s][0], placeholder="Todas", key="todas_status",
        )
        dia = st.date_input("Data", value=None, format="DD/MM/YYYY", key="todas_data")

    def corresponde(r):
        texto = " ".join([
            ctx["nomes_espacos"].get(r.get("espaco_id"), ""),
            ctx["nomes_usuarios"].get(r.get("responsavel_id"), ""),
            r.get("finalidade") or "",
        ]).lower()
        return (
            (not busca or busca in texto)
            and (not status or r.get("status") in status)
            and (not dia or (r.get("inicio") and para_local(r["inicio"]).date() == dia))
        )

    filtradas = [r for r in reservas if corresponde(r)]
    st.caption(f"{len(filtradas)} de {len(reservas)} reservas")
    for reserva in filtradas[:50]:
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="top"):
                with st.container():
                    _resumo_reserva(ctx, reserva)
                status_badge(reserva.get("status"))
            if reserva.get("motivo_rejeicao"):
                st.caption(f"Motivo da rejeição: {reserva['motivo_rejeicao']}")
            with st.expander("Histórico", icon=":material/history:"):
                _historico(ctx, reserva["id"])
            if reserva.get("status") in {"pendente", "reservada"} and para_local(reserva["fim"]) >= agora():
                if st.button("Cancelar reserva", icon=":material/event_busy:", key=f"coord_cancelar_{reserva['id']}"):
                    _concluir(*ctx["reservas"].cancelar_reserva(reserva["id"], ctx["usuario"]["id"], ctx["perfil"]))
    if len(filtradas) > 50:
        st.caption("Mostrando as 50 mais recentes. Use a pesquisa para refinar.")


def _historico(ctx, reserva_id):
    eventos = ctx["reservas"].historico_da_reserva(reserva_id, ctx["perfil"])
    if isinstance(eventos, tuple) or not eventos:
        st.caption("Sem registros.")
        return
    for evento in eventos:
        rotulo, icone = ACOES_HISTORICO.get(evento.get("acao"), (evento.get("acao"), ":material/info:"))
        quando = evento.get("created_at")
        st.markdown(
            f"{icone} **{rotulo}** por {ctx['nomes_usuarios'].get(evento.get('executado_por_id'), '—')}"
            + (f" · :gray[{formatar_data(quando)} {para_local(quando):%H:%M}]" if quando else "")
        )


# ---------------------------------------------------------------------------
# Bloqueios (RF36, RN18, RN31)

def _bloqueios(ctx):
    controller = BloqueioController()
    ativos = [e for e in ctx["espacos"] if e.get("ativo", True)]
    with st.expander("Bloquear um espaço", icon=":material/add:", expanded=False):
        if not ativos:
            st.caption("Cadastre um espaço primeiro.")
        else:
            with st.form("novo_bloqueio", clear_on_submit=True):
                espaco_id = st.selectbox(
                    "Espaço", [e["id"] for e in ativos], format_func=ctx["nomes_espacos"].get
                )
                with st.container(horizontal=True):
                    dia_ini = st.date_input("Data inicial", min_value=agora().date(), format="DD/MM/YYYY")
                    hora_ini = st.time_input("Hora inicial", value=time(0, 0), step=timedelta(minutes=30))
                with st.container(horizontal=True):
                    dia_fim = st.date_input("Data final", min_value=agora().date(), format="DD/MM/YYYY")
                    hora_fim = st.time_input("Hora final", value=time(23, 30), step=timedelta(minutes=30))
                motivo = st.text_input("Motivo", placeholder="Ex.: manutenção dos computadores")
                salvar = st.form_submit_button("Bloquear", icon=":material/block:", type="primary")
            if salvar:
                ok, resultado = controller.criar_bloqueio(
                    espaco_id=espaco_id,
                    inicio=combinar_local(dia_ini, hora_ini),
                    fim=combinar_local(dia_fim, hora_fim),
                    motivo=motivo,
                    responsavel_id=ctx["usuario"]["id"],
                    perfil=ctx["perfil"],
                )
                _concluir(ok, "Espaço bloqueado. Novas reservas nesse período serão recusadas." if ok else resultado)

    bloqueios = controller.listar_bloqueios(ctx["perfil"])
    if isinstance(bloqueios, tuple):
        st.error(bloqueios[1])
        return
    vigentes = [b for b in bloqueios if b.get("fim") and para_local(b["fim"]) >= agora()]
    if not vigentes:
        estado_vazio("Nenhum espaço bloqueado no momento.", ":material/lock_open:")
        return
    for b in sorted(vigentes, key=lambda b: b["inicio"]):
        with st.container(border=True, horizontal=True, vertical_alignment="center"):
            st.markdown(
                f"**:material/lock: {ctx['nomes_espacos'].get(b.get('espaco_id'), 'Sala removida')}**  \n"
                f"{formatar_data(b['inicio'])} {para_local(b['inicio']):%H:%M} → "
                f"{formatar_data(b['fim'])} {para_local(b['fim']):%H:%M}  \n"
                f":gray[{b.get('motivo', '')}]"
            )
            if st.button("Remover", icon=":material/lock_open:", key=f"desbloquear_{b['id']}"):
                _concluir(*controller.remover_bloqueio(b["id"], ctx["perfil"], ctx["usuario"]["id"]))


# ---------------------------------------------------------------------------
# Equipamentos (RF52, RN14, RN29)

def _equipamentos():
    controller = EquipamentoController()
    with st.form("novo_equipamento", clear_on_submit=True):
        with st.container(horizontal=True, vertical_alignment="bottom"):
            nome = st.text_input("Novo equipamento", placeholder="Ex.: Projetor")
            descricao = st.text_input("Descrição", placeholder="Opcional")
        exige = st.checkbox("Exige autorização para uso")
        if st.form_submit_button("Cadastrar equipamento", icon=":material/add:", type="primary"):
            ok, resultado = controller.criar_equipamento(nome=nome, descricao=descricao, exige_autorizacao=exige)
            _concluir(ok, f"{nome.strip()} cadastrado." if ok else resultado)

    try:
        equipamentos = controller.listar_equipamentos()
    except Exception:
        st.error("Não foi possível carregar os equipamentos.")
        return
    if not equipamentos:
        estado_vazio("Nenhum equipamento cadastrado. Ex.: Projetor, Wi-Fi, Computadores.", ":material/devices:")
        return
    st.caption("Associe equipamentos às salas em Salas e espaços › Editar.")
    for e in sorted(equipamentos, key=lambda e: e.get("nome", "").lower()):
        eid = e["id"]
        with st.container(border=True, horizontal=True, vertical_alignment="bottom"):
            novo_nome = st.text_input("Nome", value=e.get("nome", ""), key=f"eq_nome_{eid}")
            nova_desc = st.text_input("Descrição", value=e.get("descricao", ""), key=f"eq_desc_{eid}")
            exige = st.toggle("Exige autorização", value=e.get("exige_autorizacao", False), key=f"eq_aut_{eid}")
            if st.button("Salvar", icon=":material/save:", key=f"eq_salvar_{eid}"):
                _concluir(*controller.atualizar_equipamento(
                    eid, {"nome": novo_nome.strip(), "descricao": nova_desc.strip(), "exige_autorizacao": exige}
                ))
            if st.button("Remover", icon=":material/delete:", key=f"eq_remover_{eid}"):
                _concluir(*controller.excluir_equipamento(eid))


# ---------------------------------------------------------------------------
# Usuários (RF55, RN28)

def _usuarios(ctx, usuarios, controller):
    coordenador = ctx["usuario"]
    ativos = [e for e in ctx["espacos"] if e.get("ativo", True)]
    with st.container(horizontal=True, vertical_alignment="bottom"):
        busca = st.text_input(
            "Buscar usuário", placeholder="Nome, e-mail ou RA",
            icon=":material/search:", key="coord_busca_usuario",
        ).strip().lower()
        filtro_perfil = st.pills(
            "Perfil", list(PERFIS), format_func=lambda p: PERFIS[p][0],
            selection_mode="multi", key="coord_filtro_perfil",
        )

    filtrados = [
        u for u in usuarios
        if (not busca or busca in " ".join(str(u.get(c) or "") for c in ("nome", "email", "ra")).lower())
        and (not filtro_perfil or normalizar_perfil(u) in filtro_perfil)
    ]
    if not filtrados:
        estado_vazio("Nenhum usuário encontrado.", ":material/person_search:")
        return

    for u in sorted(filtrados, key=lambda u: (u.get("nome") or "").lower()):
        uid = u["id"]
        perfil_u = normalizar_perfil(u)
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"**:material/account_circle: {u.get('nome') or 'Cadastro incompleto'}**")
                perfil_badge(perfil_u)
                if not u.get("ativo", True):
                    st.badge("Inativo", icon=":material/block:", color="gray")
            st.caption(" · ".join(filter(None, [u.get("email"), f"RA {u['ra']}" if u.get("ra") else None])) or f"ID {uid}")

            if not u.get("nome") or not u.get("email"):
                st.warning("Este registro não tem nome nem e-mail (provavelmente um cadastro que falhou).", icon=":material/warning:")
                if st.button("Excluir registro", icon=":material/delete:", key=f"excluir_{uid}"):
                    _concluir(*controller.excluir_usuario(uid))
                continue

            if uid == coordenador.get("id"):
                st.caption(":material/info: Esta é a sua conta.")
                continue

            with st.container(horizontal=True, vertical_alignment="bottom"):
                novo_perfil = st.selectbox(
                    "Perfil", list(PERFIS),
                    index=list(PERFIS).index(perfil_u) if perfil_u in PERFIS else 0,
                    format_func=lambda p: PERFIS[p][0], key=f"perfil_{uid}",
                )
                ativo = st.toggle("Ativo", value=u.get("ativo", True), key=f"ativo_{uid}")
                if st.button("Salvar", icon=":material/save:", key=f"salvar_{uid}"):
                    _concluir(*controller.atualizar_usuario(uid, u["nome"], u["email"], u.get("ra"), novo_perfil, ativo))

            if perfil_u == "externo":
                autorizados = st.multiselect(
                    "Espaços autorizados",
                    [e["id"] for e in ativos],
                    default=[i for i in u.get("espacos_autorizados_ids") or [] if i in {e["id"] for e in ativos}],
                    format_func=ctx["nomes_espacos"].get,
                    placeholder="Nenhum: este usuário não consegue reservar",
                    key=f"aut_{uid}",
                )
                if st.button("Salvar autorizações", icon=":material/verified_user:", key=f"salvar_aut_{uid}"):
                    _concluir(*controller.atualizar_autorizacoes(uid, autorizados))
