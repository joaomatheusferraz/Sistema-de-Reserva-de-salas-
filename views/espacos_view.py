"""Reservar sala: busca, filtros avançados e grade de cards (protótipo do Figma)."""

from datetime import timedelta

import streamlit as st

from controllers.espaco_controller import EspacoController
from models.reserva_model import ReservaModel
from utils.ui import FUSO_LOCAL, estado_vazio, normalizar_perfil, tipo_espaco
from views.componentes import (
    carregar_equipamentos,
    carregar_ocupacao,
    grade_salas,
    nomes_equipamentos,
)
from views.reserva_dialogos import dialogo_reservar

PODEM_RESERVAR = {"professor", "externo", "coordenador"}
CAPACIDADES = {"Qualquer": 0, ">20": 21, ">50": 51, ">100": 101}


def _alternar_filtros():
    st.session_state["filtros_abertos"] = not st.session_state.get("filtros_abertos", False)


def espacos_view(usuario):
    perfil = normalizar_perfil(usuario)
    mensagem = st.session_state.pop("salas_mensagem", None) or st.session_state.pop("espaco_mensagem", None)
    if mensagem:
        st.success(mensagem, icon=":material/check_circle:")

    try:
        controller = EspacoController()
        espacos = controller.listar_espacos()
    except Exception:
        st.error("Não foi possível carregar os espaços.", icon=":material/error:")
        return
    equipamentos = carregar_equipamentos()

    # ---- Busca + botão de filtros avançados ----
    with st.container(horizontal=True, vertical_alignment="center"):
        busca = st.text_input(
            "Buscar",
            placeholder="Buscar sala, laboratório ou equipamento...",
            icon=":material/search:",
            label_visibility="collapsed",
            key="busca_salas",
        )
        st.button(
            "Filtros avançados",
            icon=":material/tune:",
            type="primary",
            key="btn_filtros",
            on_click=_alternar_filtros,
        )

    capacidade_min, blocos, filtro_equip, tipos, momento = 0, [], [], [], None
    if st.session_state.get("filtros_abertos"):
        todos_blocos = sorted({
            str((e.get("localizacao") or {}).get("bloco")).strip()
            for e in espacos if (e.get("localizacao") or {}).get("bloco")
        })
        with st.container(key="card_filtros_salas"):
            capacidade, local, equip, tipo, disponibilidade = st.columns(5, gap="medium")
            with capacidade:
                capacidade_min = CAPACIDADES[
                    st.selectbox("Capacidade", list(CAPACIDADES), key="filtro_capacidade")
                ]
            with local:
                blocos = st.multiselect(
                    "Localização", todos_blocos, format_func=lambda b: f"Bloco {b}",
                    placeholder="Todos os blocos", key="filtro_blocos",
                )
            with equip:
                filtro_equip = st.multiselect(
                    "Equipamentos", list(equipamentos),
                    format_func=lambda i: equipamentos[i]["nome"],
                    placeholder="Qualquer", key="filtro_equip",
                )
            with tipo:
                tipos = st.multiselect(
                    "Tipo", ["sala", "laboratorio"], format_func=lambda t: tipo_espaco(t)[0],
                    placeholder="Todos", key="filtro_tipo",
                )
            with disponibilidade:
                momento = st.datetime_input(
                    "Disponibilidade", value=None, format="DD/MM/YYYY",
                    step=timedelta(minutes=30), key="filtro_disponibilidade",
                    help="Mostra só as salas livres por 30 minutos a partir deste horário.",
                )
        if momento is not None and momento.tzinfo is None:
            momento = momento.replace(tzinfo=FUSO_LOCAL)

    if not espacos:
        estado_vazio(
            "Nenhum espaço ativo cadastrado. "
            + ("Cadastre a primeira sala na Área do coordenador."
               if perfil == "coordenador" else "Peça ao coordenador para cadastrar uma sala."),
            ":material/meeting_room:",
        )
        return

    reservas, erro = carregar_ocupacao()
    if erro:
        st.warning(erro)

    termo = busca.strip().lower()

    def corresponde(espaco):
        localizacao = espaco.get("localizacao") or {}
        bloco = localizacao.get("bloco")
        andar = localizacao.get("andar")
        texto = " ".join([
            str(espaco.get("nome", "")),
            f"Bloco {bloco}" if bloco else "",
            f"Andar {andar}" if andar is not None and andar != "" else "",
            str(localizacao.get("identificacao", "")),
            tipo_espaco(espaco.get("tipo"))[0],
            *(espaco.get("caracteristicas") or []),
            *nomes_equipamentos(espaco, equipamentos),
        ]).lower()
        if momento and any(
            r.get("espaco_id") == espaco["id"]
            and ReservaModel._sobrepoe(momento, momento + timedelta(minutes=30), r.get("inicio"), r.get("fim"))
            for r in reservas
        ):
            return False
        return (
            (not termo or termo in texto)
            and (not tipos or espaco.get("tipo") in tipos)
            and (not blocos or str(localizacao.get("bloco", "")).strip() in blocos)
            and (espaco.get("capacidade") or 0) >= capacidade_min
            and set(filtro_equip) <= set(espaco.get("equipamentos_ids") or [])
        )

    filtrados = [e for e in espacos if corresponde(e)]
    if not filtrados:
        estado_vazio("Nenhuma sala corresponde à busca.", ":material/search_off:")
        return

    autorizados = set(usuario.get("espacos_autorizados_ids") or [])

    def ao_reservar(espaco):
        if perfil not in PODEM_RESERVAR:
            return None
        if perfil == "externo" and espaco["id"] not in autorizados:
            return None  # RN28: externo só reserva espaços autorizados.
        return lambda e: dialogo_reservar(e, usuario, perfil, reservas)

    grade_salas(
        filtrados,
        reservas,
        "salas",
        equipamentos=equipamentos,
        ao_reservar=ao_reservar,
        motivo_sem_reserva="Sem autorização" if perfil == "externo" else None,
        ao_editar=(lambda e: _editar_espaco(e, controller, equipamentos))
        if perfil == "coordenador" else None,
    )


def _campos_espaco(prefixo, equipamentos, atual=None):
    atual = atual or {}
    localizacao = atual.get("localizacao") or {}
    nome = st.text_input("Nome", value=atual.get("nome", ""), key=f"{prefixo}_nome",
                         placeholder="Ex.: Sala 201")
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
        andar = st.text_input("Andar", value=str(localizacao.get("andar", "")), key=f"{prefixo}_andar")
        identificacao = st.text_input(
            "Número ou identificação", value=localizacao.get("identificacao", ""), key=f"{prefixo}_ident"
        )
    equipamentos_ids = st.multiselect(
        "Equipamentos",
        list(equipamentos),
        default=[i for i in atual.get("equipamentos_ids") or [] if i in equipamentos],
        format_func=lambda i: equipamentos[i]["nome"],
        placeholder="Cadastre equipamentos na Área do coordenador" if not equipamentos else "Selecione",
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
        "localizacao": {
            "bloco": bloco.strip(),
            "andar": andar.strip(),
            "identificacao": identificacao.strip(),
        },
        "caracteristicas": [c.strip() for c in caracteristicas.split(",") if c.strip()],
        "equipamentos_ids": equipamentos_ids,
        "regras_especificas": [r.strip() for r in regras.splitlines() if r.strip()],
    }


@st.dialog("Criar nova sala", width="large")
def dialogo_nova_sala():
    try:
        controller = EspacoController()
    except Exception:
        st.error("Não foi possível conectar ao banco de dados.")
        return
    equipamentos = carregar_equipamentos()
    with st.form("cadastrar_espaco", clear_on_submit=True, border=False):
        dados = _campos_espaco("novo", equipamentos)
        cadastrar = st.form_submit_button("Cadastrar", icon=":material/add:", type="primary")
    if cadastrar:
        sucesso, mensagem = controller.criar_espaco(**dados)
        if sucesso:
            st.session_state["coord_mensagem"] = f"{dados['nome']} cadastrado com sucesso."
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
