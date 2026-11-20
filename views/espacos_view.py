from datetime import time, timedelta

import streamlit as st

from controllers.espaco_controller import EspacoController
from models.reserva_model import ReservaModel
from utils.ui import (
    agora,
    cabecalho,
    combinar_local,
    estado_vazio,
    normalizar_perfil,
    tipo_espaco,
)
from views.componentes import (
    carregar_equipamentos,
    carregar_ocupacao,
    grade_salas,
    nomes_equipamentos,
)


def espacos_view(usuario):
    cabecalho(
        "Salas e espaços",
        "Pesquise por capacidade, equipamento ou horário livre e reserve em um clique.",
        ":material/meeting_room:",
    )
    perfil = normalizar_perfil(usuario)
    if mensagem := st.session_state.pop("espaco_mensagem", None):
        st.success(mensagem, icon=":material/check_circle:")

    try:
        controller = EspacoController()
    except Exception:
        st.error("Não foi possível carregar os espaços.", icon=":material/error:")
        return

    equipamentos = carregar_equipamentos()
    if perfil == "coordenador":
        with st.expander("Cadastrar nova sala ou laboratório", icon=":material/add_business:"):
            _formulario_espaco(controller, equipamentos)

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

    # ---- Filtros (seção 14 do documento) ----
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="bottom"):
            busca = st.text_input(
                "Buscar",
                placeholder="Nome, bloco ou característica",
                icon=":material/search:",
                key="espacos_busca",
            )
            capacidade_min = st.number_input(
                "Mínimo de lugares", min_value=0, step=5, value=0, key="espacos_capacidade"
            )
        with st.container(horizontal=True, vertical_alignment="bottom"):
            tipos = st.pills(
                "Tipo",
                ["sala", "laboratorio"],
                format_func=lambda t: tipo_espaco(t)[0],
                selection_mode="multi",
                key="espacos_tipos",
            )
            if equipamentos:
                filtro_equip = st.multiselect(
                    "Equipamentos",
                    list(equipamentos),
                    format_func=lambda i: equipamentos[i]["nome"],
                    placeholder="Precisa ter…",
                    key="espacos_equipamentos",
                )
            else:
                filtro_equip = []
        livre = st.toggle(
            "Somente salas livres em um horário",
            key="espacos_livre",
        )
        periodo = None
        if livre:
            with st.container(horizontal=True):
                dia = st.date_input("Dia", min_value=agora().date(), format="DD/MM/YYYY", key="espacos_dia")
                inicio = st.time_input("De", value=time(19, 0), step=timedelta(minutes=30), key="espacos_ini")
                fim = st.time_input("Até", value=time(21, 0), step=timedelta(minutes=30), key="espacos_fim")
            periodo = (combinar_local(dia, inicio), combinar_local(dia, fim))

    reservas, erro = carregar_ocupacao()
    if erro:
        st.warning(erro)

    termo = busca.strip().lower()

    def corresponde(espaco):
        texto = " ".join([
            str(espaco.get("nome", "")),
            str((espaco.get("localizacao") or {}).get("bloco", "")),
            str((espaco.get("localizacao") or {}).get("identificacao", "")),
            *(espaco.get("caracteristicas") or []),
            *nomes_equipamentos(espaco, equipamentos),
        ]).lower()
        ids_sala = set(espaco.get("equipamentos_ids") or [])
        if periodo and any(
            r.get("espaco_id") == espaco["id"]
            and ReservaModel._sobrepoe(periodo[0], periodo[1], r.get("inicio"), r.get("fim"))
            for r in reservas
        ):
            return False
        return (
            (not termo or termo in texto)
            and (not tipos or espaco.get("tipo") in tipos)
            and (espaco.get("capacidade") or 0) >= capacidade_min
            and set(filtro_equip) <= ids_sala
        )

    filtrados = [e for e in espacos if corresponde(e)]
    st.caption(f"{len(filtrados)} de {len(espacos)} espaços")
    if not filtrados:
        estado_vazio("Nenhuma sala corresponde aos filtros.", ":material/search_off:")
        return

    grade_salas(
        filtrados,
        reservas,
        "espacos",
        perfil in {"professor", "externo", "coordenador"},
        equipamentos=equipamentos,
        ao_editar=(lambda e: _editar_espaco(e, controller, equipamentos))
        if perfil == "coordenador" else None,
    )


def _campos_espaco(prefixo, equipamentos, atual=None):
    atual = atual or {}
    localizacao = atual.get("localizacao") or {}
    nome = st.text_input("Nome", value=atual.get("nome", ""), key=f"{prefixo}_nome")
    with st.container(horizontal=True):
        tipo = st.selectbox(
            "Tipo",
            ["sala", "laboratorio"],
            index=["sala", "laboratorio"].index(atual.get("tipo", "sala")) if atual.get("tipo") in ("sala", "laboratorio") else 0,
            format_func=lambda valor: tipo_espaco(valor)[0],
            key=f"{prefixo}_tipo",
        )
        capacidade = st.number_input(
            "Capacidade", min_value=1, step=1, value=int(atual.get("capacidade") or 20), key=f"{prefixo}_cap"
        )
    with st.container(horizontal=True):
        bloco = st.text_input("Bloco", value=localizacao.get("bloco", ""), key=f"{prefixo}_bloco")
        identificacao = st.text_input(
            "Número ou identificação", value=localizacao.get("identificacao", ""), key=f"{prefixo}_ident"
        )
    equipamentos_ids = st.multiselect(
        "Equipamentos",
        list(equipamentos),
        default=[i for i in atual.get("equipamentos_ids") or [] if i in equipamentos],
        format_func=lambda i: equipamentos[i]["nome"],
        placeholder="Cadastre equipamentos na Coordenação" if not equipamentos else "Selecione",
        key=f"{prefixo}_equip",
    )
    caracteristicas = st.text_input(
        "Outras características",
        value=", ".join(atual.get("caracteristicas") or []),
        placeholder="Ar-condicionado, acessível, cadeiras móveis",
        key=f"{prefixo}_carac",
    )
    regras = st.text_area(
        "Regras de uso",
        value="\n".join(atual.get("regras_especificas") or []),
        placeholder="Uma regra por linha (ex.: proibido alimentos)",
        key=f"{prefixo}_regras",
    )
    return {
        "nome": nome,
        "tipo": tipo,
        "capacidade": int(capacidade),
        "localizacao": {"bloco": bloco.strip(), "identificacao": identificacao.strip()},
        "caracteristicas": [c.strip() for c in caracteristicas.split(",") if c.strip()],
        "equipamentos_ids": equipamentos_ids,
        "regras_especificas": [r.strip() for r in regras.splitlines() if r.strip()],
    }


def _formulario_espaco(controller, equipamentos):
    with st.form("cadastrar_espaco", clear_on_submit=True):
        dados = _campos_espaco("novo", equipamentos)
        cadastrar = st.form_submit_button("Cadastrar", icon=":material/add:", type="primary")
    if cadastrar:
        sucesso, mensagem = controller.criar_espaco(**dados)
        if sucesso:
            st.session_state["espaco_mensagem"] = f"{dados['nome']} cadastrado com sucesso."
            st.rerun()
        st.error(mensagem)


@st.dialog("Editar espaço", width="large")
def _editar_espaco(espaco, controller, equipamentos):
    dados = _campos_espaco(f"edit_{espaco['id']}", equipamentos, espaco)
    with st.container(horizontal=True):
        if st.button("Salvar alterações", icon=":material/save:", type="primary"):
            ok, mensagem = controller.atualizar_espaco(espaco["id"], dados)
            if ok:
                st.session_state["espaco_mensagem"] = mensagem
                st.rerun()
            st.error(mensagem)
        if st.button("Desativar espaço", icon=":material/visibility_off:"):
            ok, mensagem = controller.excluir_espaco(espaco["id"])
            if ok:
                st.session_state["espaco_mensagem"] = mensagem
                st.rerun()
            st.error(mensagem)
    st.caption("Um espaço desativado some das buscas e não recebe novas reservas; o histórico é mantido.")
