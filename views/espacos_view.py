import streamlit as st

from controllers.espaco_controller import EspacoController
from utils.ui import cabecalho, estado_vazio, normalizar_perfil, tipo_espaco
from views.componentes import carregar_ocupacao, grade_salas


def espacos_view(usuario):
    cabecalho(
        "Salas e espaços",
        "Veja a situação de cada sala agora e reserve em um clique.",
        ":material/meeting_room:",
    )
    controller = EspacoController()
    perfil = normalizar_perfil(usuario)

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
                    st.toast("Sala cadastrada com sucesso.", icon=":material/check_circle:")
                    st.rerun()
                else:
                    st.error(mensagem)

    try:
        espacos = controller.listar_espacos()
    except Exception:
        st.error("Não foi possível carregar os espaços.", icon=":material/error:")
        return

    if not espacos:
        estado_vazio(
            "Nenhum espaço ativo cadastrado. "
            + ("Use o formulário acima para cadastrar a primeira sala."
               if perfil == "coordenador" else "Peça ao coordenador para cadastrar uma sala."),
            ":material/meeting_room:",
        )
        return

    with st.container(horizontal=True, vertical_alignment="bottom"):
        busca = st.text_input(
            "Buscar",
            placeholder="Nome, bloco ou característica",
            icon=":material/search:",
            key="espacos_busca",
        )
        tipos = st.pills(
            "Tipo",
            ["sala", "laboratorio"],
            format_func=lambda t: tipo_espaco(t)[0],
            selection_mode="multi",
            key="espacos_tipos",
        )
        capacidade_min = st.number_input(
            "Mínimo de lugares", min_value=0, step=5, value=0, key="espacos_capacidade"
        )

    termo = busca.strip().lower()

    def corresponde(espaco):
        texto = " ".join([
            str(espaco.get("nome", "")),
            str((espaco.get("localizacao") or {}).get("bloco", "")),
            str((espaco.get("localizacao") or {}).get("identificacao", "")),
            *(espaco.get("caracteristicas") or []),
        ]).lower()
        return (
            (not termo or termo in texto)
            and (not tipos or espaco.get("tipo") in tipos)
            and (espaco.get("capacidade") or 0) >= capacidade_min
        )

    filtrados = [e for e in espacos if corresponde(e)]
    st.caption(f"{len(filtrados)} de {len(espacos)} espaços")
    if not filtrados:
        estado_vazio("Nenhuma sala corresponde aos filtros.", ":material/search_off:")
        return

    reservas, erro = carregar_ocupacao()
    if erro:
        st.warning(erro)
    grade_salas(filtrados, reservas, "espacos", perfil in {"professor", "externo"})
