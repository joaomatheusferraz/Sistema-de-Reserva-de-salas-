"""Blocos visuais reutilizados pelas telas (cards de sala, carregamento de dados)."""

from collections import Counter

import streamlit as st

from controllers.bloqueio_controller import BloqueioController
from controllers.equipamento_controller import EquipamentoController
from controllers.espaco_controller import EspacoController
from controllers.reserva_controller import ReservaController
from utils.ui import (
    ir_para,
    localizacao_texto,
    pagina_disponivel,
    situacao_sala,
    tipo_espaco,
)


def carregar_espacos(apenas_ativos=True):
    try:
        return EspacoController().listar_espacos(apenas_ativos=apenas_ativos), None
    except Exception:
        return [], "Não foi possível carregar as salas do banco de dados."


def carregar_ocupacao():
    """Tudo que ocupa horário: reservas pendentes/confirmadas e bloqueios.

    Bloqueios entram com status "bloqueado" para que cards, agenda e
    formulário de reserva os tratem como mais um período indisponível.
    """
    try:
        reservas = ReservaController().listar_calendario()
    except Exception:
        return [], "Não foi possível carregar a agenda. Tente novamente mais tarde."
    if isinstance(reservas, tuple):
        return [], reservas[1]
    try:
        bloqueios = BloqueioController().listar_vigentes()
    except Exception:
        bloqueios = []
    ocupacao = list(reservas or []) + [
        {
            "id": b["id"],
            "espaco_id": b.get("espaco_id"),
            "inicio": b.get("inicio"),
            "fim": b.get("fim"),
            "status": "bloqueado",
            "motivo": b.get("motivo"),
            "bloqueio": True,
        }
        for b in bloqueios
        if b.get("inicio") and b.get("fim")
    ]
    return sorted(ocupacao, key=lambda r: r["inicio"]), None


def carregar_equipamentos(apenas_ativos=True):
    try:
        return {
            e["id"]: e for e in EquipamentoController().listar_equipamentos(apenas_ativos)
        }
    except Exception:
        return {}


def nomes_equipamentos(espaco, equipamentos):
    return [
        equipamentos[i]["nome"]
        for i in espaco.get("equipamentos_ids") or []
        if i in equipamentos
    ]


def rotulos_unicos(espacos):
    """Nome de cada sala; salas homônimas recebem a localização (e o id, se preciso)."""
    repeticoes = Counter(e.get("nome") for e in espacos)
    rotulos = {
        e["id"]: e.get("nome") if repeticoes[e.get("nome")] == 1
        else f"{e.get('nome')} · {localizacao_texto(e)}"
        for e in espacos
    }
    repeticoes = Counter(rotulos.values())
    return {
        espaco_id: rotulo if repeticoes[rotulo] == 1 else f"{rotulo} ({espaco_id})"
        for espaco_id, rotulo in rotulos.items()
    }


def card_sala(espaco, reservas, chave, permite_reservar, equipamentos=None, ao_editar=None):
    """Card com ícone, situação atual e botões de ação de uma sala."""
    rotulo_tipo, icone_tipo = tipo_espaco(espaco.get("tipo"))
    situacao, icone_sit, cor_sit, detalhe = situacao_sala(espaco["id"], reservas)

    with st.container(border=True, height="stretch"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown(f"#### {icone_tipo} {espaco.get('nome', 'Sem nome')}")
        with st.container(horizontal=True, gap="small"):
            st.badge(situacao, icon=icone_sit, color=cor_sit)
            st.badge(rotulo_tipo, icon=icone_tipo, color="blue")
        st.caption(detalhe)
        st.markdown(
            f":material/groups: **{espaco.get('capacidade', '—')}** lugares  \n"
            f":material/location_on: {localizacao_texto(espaco)}"
        )
        equipamentos_sala = nomes_equipamentos(espaco, equipamentos or {})
        if equipamentos_sala:
            st.markdown(" ".join(f":blue-badge[{nome}]" for nome in equipamentos_sala))
        caracteristicas = espaco.get("caracteristicas") or []
        if caracteristicas:
            st.caption(" · ".join(caracteristicas))

        with st.container(horizontal=True, gap="small"):
            if permite_reservar and pagina_disponivel("reservas"):
                if st.button(
                    "Reservar",
                    icon=":material/add_circle:",
                    type="primary",
                    key=f"reservar_{chave}_{espaco['id']}",
                    width="stretch",
                ):
                    ir_para("reservas", reserva_espaco_id=espaco["id"])
            if st.button(
                "Ver agenda",
                icon=":material/calendar_month:",
                key=f"agenda_{chave}_{espaco['id']}",
                width="stretch",
            ):
                ir_para("calendario", agenda_espaco_id=espaco["id"])
            if ao_editar and st.button(
                "Editar",
                icon=":material/edit:",
                key=f"editar_{chave}_{espaco['id']}",
                width="stretch",
            ):
                ao_editar(espaco)


def grade_salas(espacos, reservas, chave, permite_reservar, colunas=3,
                equipamentos=None, ao_editar=None):
    for inicio in range(0, len(espacos), colunas):
        linha = st.columns(colunas)
        for coluna, espaco in zip(linha, espacos[inicio:inicio + colunas]):
            with coluna:
                card_sala(espaco, reservas, chave, permite_reservar, equipamentos, ao_editar)
