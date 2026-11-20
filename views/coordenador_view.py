import streamlit as st

from controllers.espaco_controller import EspacoController
from controllers.reserva_controller import ReservaController
from controllers.usuario_controller import UsuarioController
from utils.ui import (
    PERFIS,
    cabecalho,
    estado_vazio,
    formatar_periodo,
    normalizar_perfil,
    perfil_badge,
)


def coordenador_view(usuario):
    perfil = normalizar_perfil(usuario)
    if perfil != "coordenador":
        st.error("Acesso restrito ao coordenador.", icon=":material/lock:")
        return

    cabecalho(
        "Coordenação",
        "Analise as solicitações de reserva e gerencie os usuários.",
        ":material/fact_check:",
    )
    if mensagem := st.session_state.pop("coord_mensagem", None):
        st.toast(mensagem, icon=":material/check_circle:")

    reserva_controller = ReservaController()
    usuario_controller = UsuarioController()
    espacos = EspacoController().listar_espacos(apenas_ativos=False)
    usuarios = usuario_controller.listar_usuarios()
    pendentes = reserva_controller.listar_pendentes(perfil)
    if isinstance(pendentes, tuple):
        st.error(pendentes[1])
        pendentes = []

    aba_solicitacoes, aba_usuarios = st.tabs([
        f":material/pending_actions: Solicitações ({len(pendentes)})",
        f":material/group: Usuários ({len(usuarios)})",
    ])
    with aba_solicitacoes:
        _solicitacoes(usuario, perfil, pendentes, espacos, usuarios, reserva_controller)
    with aba_usuarios:
        _usuarios(usuario, usuarios, usuario_controller)


def _solicitacoes(usuario, perfil, pendentes, espacos, usuarios, controller):
    if not pendentes:
        estado_vazio("Nenhuma solicitação pendente. Tudo em dia!", ":material/task_alt:")
        return

    nomes_espacos = {e["id"]: e.get("nome", e["id"]) for e in espacos}
    nomes_usuarios = {u["id"]: u.get("nome") or "Sem nome" for u in usuarios}

    for reserva in sorted(pendentes, key=lambda r: r["inicio"]):
        rid = reserva["id"]
        with st.container(border=True):
            st.markdown(
                f"**:material/meeting_room: {nomes_espacos.get(reserva.get('espaco_id'), 'Sala removida')}**  \n"
                f":material/schedule: {formatar_periodo(reserva['inicio'], reserva['fim'])}  \n"
                f":material/person: {nomes_usuarios.get(reserva.get('responsavel_id'), 'Usuário removido')}"
            )
            if reserva.get("finalidade"):
                st.caption(f"Finalidade: {reserva['finalidade']}")
            with st.container(horizontal=True, gap="small"):
                if st.button("Aprovar", icon=":material/check_circle:", type="primary", key=f"aprovar_{rid}"):
                    ok, mensagem = controller.aprovar_reserva(rid, usuario["id"], perfil)
                    if ok:
                        st.session_state["coord_mensagem"] = mensagem
                        st.rerun()
                    st.error(mensagem)
                if st.button("Rejeitar", icon=":material/cancel:", key=f"rejeitar_{rid}"):
                    _rejeitar(rid, usuario, perfil, controller)


@st.dialog("Rejeitar solicitação")
def _rejeitar(reserva_id, usuario, perfil, controller):
    motivo = st.text_area("Motivo da rejeição", placeholder="Ex.: sala reservada para evento da coordenação")
    if st.button("Confirmar rejeição", icon=":material/cancel:", type="primary"):
        ok, mensagem = controller.rejeitar_reserva(reserva_id, usuario["id"], perfil, motivo)
        if ok:
            st.session_state["coord_mensagem"] = mensagem
            st.rerun()
        st.error(mensagem)


def _usuarios(coordenador, usuarios, controller):
    busca = st.text_input(
        "Buscar usuário",
        placeholder="Nome, e-mail ou RA",
        icon=":material/search:",
        key="coord_busca_usuario",
    ).strip().lower()

    filtrados = [
        u for u in usuarios
        if not busca or busca in " ".join(
            str(u.get(c) or "") for c in ("nome", "email", "ra")
        ).lower()
    ]
    if not filtrados:
        estado_vazio("Nenhum usuário encontrado.", ":material/person_search:")
        return

    for u in sorted(filtrados, key=lambda u: (u.get("nome") or "").lower()):
        uid = u["id"]
        incompleto = not u.get("nome") or not u.get("email")
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"**:material/account_circle: {u.get('nome') or 'Cadastro incompleto'}**")
                perfil_badge(normalizar_perfil(u))
                if not u.get("ativo", True):
                    st.badge("Inativo", icon=":material/block:", color="gray")
            st.caption(" · ".join(filter(None, [u.get("email"), f"RA {u['ra']}" if u.get("ra") else None])) or f"ID {uid}")

            if incompleto:
                st.warning(
                    "Este registro não tem nome nem e-mail (provavelmente um cadastro que falhou).",
                    icon=":material/warning:",
                )
                if st.button("Excluir registro", icon=":material/delete:", key=f"excluir_{uid}"):
                    ok, mensagem = controller.excluir_usuario(uid)
                    if ok:
                        st.session_state["coord_mensagem"] = mensagem
                        st.rerun()
                    st.error(mensagem)
                continue

            if uid == coordenador.get("id"):
                st.caption(":material/info: Esta é a sua conta.")
                continue

            with st.container(horizontal=True, vertical_alignment="bottom"):
                novo_perfil = st.selectbox(
                    "Perfil",
                    list(PERFIS),
                    index=list(PERFIS).index(normalizar_perfil(u)) if normalizar_perfil(u) in PERFIS else 0,
                    format_func=lambda p: PERFIS[p][0],
                    key=f"perfil_{uid}",
                )
                ativo = st.toggle("Ativo", value=u.get("ativo", True), key=f"ativo_{uid}")
                if st.button("Salvar", icon=":material/save:", key=f"salvar_{uid}"):
                    ok, mensagem = controller.atualizar_usuario(
                        uid, u["nome"], u["email"], u.get("ra"), novo_perfil, ativo
                    )
                    if ok:
                        st.session_state["coord_mensagem"] = mensagem
                        st.rerun()
                    st.error(mensagem)
