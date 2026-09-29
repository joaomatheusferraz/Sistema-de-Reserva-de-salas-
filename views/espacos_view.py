import streamlit as st

from controllers.espaco_controller import EspacoController


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
        if perfil == "coordenador":
            st.info("Nenhum espaço ativo cadastrado. Use o formulário acima para cadastrar a primeira sala.")
        else:
            st.info("Nenhum espaço ativo cadastrado. Peça ao coordenador para cadastrar uma sala.")
        return

    for espaco in espacos:
        with st.expander(f"{espaco.get('nome')} - {espaco.get('tipo')}"):
            st.write(f"Capacidade: {espaco.get('capacidade')}")
            localizacao = espaco.get("localizacao", {})
            bloco = localizacao.get("bloco") or "Não informado"
            identificacao = localizacao.get("identificacao") or "Não informada"
            st.write(f"Localização: bloco {bloco}, identificação {identificacao}")
            st.write(", ".join(espaco.get("caracteristicas", [])) or "Sem características informadas.")
