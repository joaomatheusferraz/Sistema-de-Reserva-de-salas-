import streamlit as st

from controllers.espaco_controller import EspacoController
from utils.ui import localizacao_texto, tipo_espaco


def espacos_view(usuario):
    st.title("Espaços")
    controller = EspacoController()
    perfil = str(usuario.get("perfil", "aluno")).strip().lower()

    if perfil == "coordenador":
        with st.expander("Cadastrar nova sala", icon=":material/add_business:"):
            with st.form("cadastrar_espaco"):
                nome = st.text_input("Nome da sala")
                tipo = st.selectbox(
                    "Tipo",
                    ["sala", "laboratorio"],
                    format_func=lambda valor: tipo_espaco(valor)[0],
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
        if perfil == "coordenador":
            st.info("Nenhum espaço ativo cadastrado. Use o formulário acima para cadastrar a primeira sala.")
        else:
            st.info("Nenhum espaço ativo cadastrado. Peça ao coordenador para cadastrar uma sala.")
        return

    for espaco in espacos:
        tipo, icone = tipo_espaco(espaco.get("tipo") or "Tipo não informado")
        with st.expander(f"{espaco.get('nome')} · {tipo}", icon=icone):
            st.write(f"Capacidade: {espaco.get('capacidade')}")
            st.caption(localizacao_texto(espaco))
            st.write(", ".join(espaco.get("caracteristicas", [])) or "Sem características informadas.")
