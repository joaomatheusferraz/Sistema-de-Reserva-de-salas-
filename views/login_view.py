import streamlit as st

from controllers.auth_controller import AuthController


def login_view():
    st.markdown(
        """
        <style>
            .login-shell {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(180deg, #f3f5f9 0%, #eef2f7 100%);
                padding: 1.5rem;
            }
            .login-card {
                width: min(100%, 980px);
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(77, 28, 114, 0.08);
                border-radius: 22px;
                box-shadow: 0 18px 40px rgba(30,41,59,0.12);
                overflow: hidden;
            }
            .login-left {
                background: linear-gradient(180deg, #4d1c72 0%, #3b155c 100%);
                color: white;
                padding: 2.5rem 2rem;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .login-title {
                font-size: 2.2rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }
            .login-subtitle {
                font-size: 1rem;
                opacity: 0.9;
                margin-bottom: 1.5rem;
            }
            .login-feature {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-size: 1rem;
                margin: 0.5rem 0;
                opacity: 0.95;
            }
            .login-right {
                padding: 2.5rem 2.2rem;
            }
            .login-form-wrap {
                max-width: 420px;
                margin: 0 auto;
            }
            .login-label {
                font-size: 0.95rem;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 0.35rem;
            }
            .button-primary {
                background: linear-gradient(135deg, #4d1c72, #6c2ab0);
                border: none;
                border-radius: 12px;
                padding: 0.8rem 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="login-shell">
            <div class="login-card">
                <div style="display:grid; grid-template-columns: 1fr 1.1fr;">
                    <div class="login-left">
                        <div style="font-size: 1.8rem; font-weight: 800; margin-bottom: 0.8rem;">UniReserve</div>
                        <div class="login-title">Bem-vindo</div>
                        <div class="login-subtitle">Sistema de reservas de salas e laboratórios</div>
                        <div class="login-feature">✅ Consulta de espaços</div>
                        <div class="login-feature">✅ Reservas e aprovações</div>
                        <div class="login-feature">✅ Organização acadêmica</div>
                    </div>
                    <div class="login-right">
                        <div class="login-form-wrap">
                            <h2 style="margin:0 0 1.2rem; color:#1f2937; font-weight:800;">Acessar conta</h2>
                            <form>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("<div style='max-width:520px; margin: 0 auto; padding-top: 1.5rem;'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("<div style='max-width: 420px; margin: 0 auto;'>", unsafe_allow_html=True)
            ra = st.text_input("RA", key="login_ra", placeholder="Digite seu RA")
            senha = st.text_input("Senha", type="password", key="login_senha", placeholder="Digite sua senha")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

        if entrar:
            sucesso, mensagem = AuthController().login(ra, senha)
            if sucesso:
                st.rerun()
            st.error(mensagem)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        with st.expander("Ainda não tenho cadastro", expanded=False):
            with st.form("cadastro_form"):
                nome = st.text_input("Nome completo", key="cadastro_nome")
                email = st.text_input("E-mail", key="cadastro_email")
                novo_ra = st.text_input("RA", key="cadastro_ra")
                perfil = st.selectbox(
                    "Perfil",
                    ["aluno", "professor", "externo"],
                    format_func=lambda valor: {
                        "aluno": "Aluno",
                        "professor": "Professor",
                        "externo": "Usuário externo",
                    }[valor],
                    key="cadastro_perfil",
                )
                nova_senha = st.text_input("Senha", type="password", key="cadastro_senha")
                cadastrar = st.form_submit_button("Criar conta")
            if cadastrar:
                sucesso, mensagem = AuthController().registrar(
                    nome, email, novo_ra, nova_senha, perfil
                )
                (st.success if sucesso else st.error)(mensagem)

        st.markdown("</div>", unsafe_allow_html=True)
