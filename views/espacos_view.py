import streamlit as st

from controllers.espaco_controller import EspacoController


def espacos_view(usuario):
    st.markdown(
        """
        <style>
            .page-title {
                font-size: 2.5rem;
                font-weight: 800;
                color: #1f2430;
                margin-bottom: 0.5rem;
            }
            .space-card {
                background: rgba(255,255,255,0.84);
                border: 1px solid rgba(31,36,48,0.08);
                border-radius: 18px;
                padding: 1.2rem 1.2rem 1rem;
                box-shadow: 0 10px 20px rgba(31, 41, 59, 0.06);
                margin-bottom: 1rem;
            }
            .space-card h4 {
                margin: 0 0 0.5rem 0;
                font-size: 1.25rem;
                color: #1f2430;
            }
            .tag {
                display: inline-block;
                padding: 0.35rem 0.75rem;
                border-radius: 999px;
                background: #f0e7ff;
                color: #4d1c72;
                font-size: 0.72rem;
                font-weight: 700;
                margin-right: 0.5rem;
                margin-bottom: 0.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='page-title'>Espaços</div>", unsafe_allow_html=True)

    controller = EspacoController()

    if usuario.get("perfil") == "coordenador":
        with st.expander("Cadastrar nova sala", icon=":material/add_business:"):
            with st.form("cadastrar_espaco"):
                nome = st.text_input("Nome da sala")
                tipo = st.selectbox(
                    "Tipo",
                    ["sala", "laboratorio"],
                    format_func=lambda valor: {
                        "sala": "Sala",
                        "laboratorio": "Laboratório",
                    }[valor],
                )
                capacidade = st.number_input(
                    "Capacidade",
                    min_value=1,
                    step=1,
                    value=20,
                )
                bloco = st.text_input("Bloco")
                identificacao = st.text_input("Número ou identificação")
                caracteristicas_texto = st.text_input(
                    "Características",
                    placeholder="Projetor, ar-condicionado, quadro branco",
                )
                cadastrar = st.form_submit_button(
                    "Cadastrar sala",
                    type="primary",
                )
            if cadastrar:
                caracteristicas = [
                    item.strip()
                    for item in caracteristicas_texto.split(",")
                    if item.strip()
                ]
                sucesso, mensagem = controller.criar_espaco(
                    nome=nome,
                    tipo=tipo,
                    capacidade=int(capacidade),
                    localizacao={
                        "bloco": bloco.strip(),
                        "identificacao": identificacao.strip(),
                    },
                    caracteristicas=caracteristicas,
                )
                if sucesso:
                    st.success("Sala cadastrada com sucesso.")
                    st.rerun()
                else:
                    st.error(mensagem)

    try:
        espacos = controller.listar_espacos()
    except Exception:
        st.error("Não foi possível carregar os espaços.")
        return

    if not espacos:
        st.info("Nenhum espaço ativo cadastrado.")
        return

    for espaco in espacos:
        localizacao = espaco.get("localizacao", {})
        bloco = localizacao.get("bloco") or "Não informado"
        identificacao = localizacao.get("identificacao") or "Não informada"
        caracteristicas = espaco.get("caracteristicas", [])

        st.markdown(
            f"""
            <div class="space-card">
                <h4>{espaco.get('nome', 'Espaço')}</h4>
                <div>
                    <span class="tag">{espaco.get('tipo', 'sala').title()}</span>
                    <span class="tag">Capacidade: {espaco.get('capacidade', 0)}</span>
                </div>
                <p style="margin: 0.9rem 0 0.2rem; color: #3b4252;">📍 Bloco {bloco} · {identificacao}</p>
                <p style="margin: 0.2rem 0 0.6rem; color: #3b4252;">{', '.join(caracteristicas) if caracteristicas else 'Sem características informadas.'}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
