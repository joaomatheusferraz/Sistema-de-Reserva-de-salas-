"""Meu perfil: dados pessoais e ações da conta (protótipo do Figma)."""

from html import escape

import streamlit as st

from controllers.auth_controller import AuthController
from controllers.usuario_controller import UsuarioController
from utils.session import iniciar_sessao
from utils.ui import avatar_html, ir_para, normalizar_perfil, rotulo_perfil


def perfil_view(usuario):
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        if st.button("", icon=":material/arrow_back_ios_new:", type="tertiary", key="voltar", help="Voltar ao início"):
            ir_para("inicio")
        st.title("Meu perfil", anchor=False)

    if mensagem := st.session_state.pop("perfil_mensagem", None):
        st.success(mensagem, icon=":material/check_circle:")

    info, acoes = st.columns([3.3, 1], gap="medium")
    with info:
        with st.container(key="card_info"):
            with st.container(key="titulo_card_info"):
                st.markdown("**Informações pessoais**")
            with st.container(horizontal=True, gap="large"):
                st.html(avatar_html(usuario.get("nome"), 116), width="content")
                campos = [
                    ("Nome", usuario.get("nome")),
                    ("RA", usuario.get("ra")),
                    ("E-mail", usuario.get("email")),
                    ("Telefone", usuario.get("telefone")),
                    ("Curso", usuario.get("curso")),
                    ("Perfil", rotulo_perfil(normalizar_perfil(usuario))),
                ]
                st.html(
                    "".join(
                        f'<p class="ur-campo-rotulo">{rotulo}</p>'
                        f'<p class="ur-campo-valor">{escape(str(valor or "—"))}</p>'
                        for rotulo, valor in campos
                    ),
                    width="stretch",
                )

    with acoes:
        with st.container(key="card_acoes"):
            with st.container(key="titulo_card_acoes"):
                st.markdown("**Ações da conta**")
            if st.button("Editar e-mail/telefone", icon=":material/edit_square:",
                         key="perfil_acao_contato", width="stretch"):
                _editar_contato(usuario)
            if st.button("Alterar senha", icon=":material/key:",
                         key="perfil_acao_senha", width="stretch"):
                _alterar_senha(usuario)
            st.button("Sair", icon=":material/logout:", type="primary",
                      key="perfil_sair", width="stretch", on_click=AuthController.logout)


@st.dialog("Editar e-mail/telefone")
def _editar_contato(usuario):
    with st.form("form_contato", border=False):
        email = st.text_input("E-mail", value=usuario.get("email") or "", icon=":material/mail:")
        telefone = st.text_input(
            "Telefone", value=usuario.get("telefone") or "",
            placeholder="(11) 91234-5678", icon=":material/call:",
        )
        salvar = st.form_submit_button("Salvar", icon=":material/save:", type="primary", width="stretch")
    if salvar:
        ok, mensagem = UsuarioController().atualizar_contato(usuario, email, telefone)
        if not ok:
            st.error(mensagem, icon=":material/error:")
            return
        iniciar_sessao({**usuario, "email": email.strip(), "telefone": telefone.strip()})
        st.session_state["perfil_mensagem"] = mensagem
        st.rerun()


@st.dialog("Alterar senha", icon=":material/lock_reset:")
def _alterar_senha(usuario):
    st.markdown(
        f"Vamos enviar um link para **{usuario.get('email') or 'o seu e-mail'}**. "
        "Abra o link para criar a nova senha."
    )
    if st.button("Enviar link", icon=":material/send:", type="primary", width="stretch"):
        with st.spinner("Enviando..."):
            ok, mensagem = AuthController().esqueci_senha(usuario.get("ra") or "")
        if ok:
            st.success(mensagem, icon=":material/mark_email_read:")
        else:
            st.error(mensagem, icon=":material/error:")
