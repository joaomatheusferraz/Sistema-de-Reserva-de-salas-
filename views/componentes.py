"""Blocos visuais reutilizados pelas telas (cards de sala, carregamento de dados)."""

from collections import Counter
from html import escape

import streamlit as st

from controllers.bloqueio_controller import BloqueioController
from controllers.equipamento_controller import EquipamentoController
from controllers.espaco_controller import EspacoController
from controllers.reserva_controller import ReservaController
from utils.ui import (
    iniciais,
    ir_para,
    localizacao_texto,
    rotulo_perfil,
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
        return [], "Não foi possível carregar os bloqueios das salas. Tente novamente mais tarde."
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


ICONES_EQUIPAMENTO = [
    # (trecho do nome, ícone Material Symbols)
    ("projetor", "videocam"),
    ("wi-fi", "wifi"),
    ("wifi", "wifi"),
    ("lousa", "crop_portrait"),
    ("quadro", "crop_portrait"),
    ("comput", "computer"),
    ("pc", "computer"),
    ("som", "speaker"),
    ("microfone", "mic"),
    ("tv", "tv"),
    ("ar-cond", "ac_unit"),
    ("ar cond", "ac_unit"),
]


def icone_equipamento(nome):
    nome = str(nome).lower()
    for trecho, icone in ICONES_EQUIPAMENTO:
        if trecho in nome:
            return icone
    return "check_circle"


def _equipamentos_html(nomes):
    itens = "".join(
        f'<span><span class="ur-icone">'
        f'{icone_equipamento(nome)}</span>{escape(nome)}</span>'
        for nome in nomes
    )
    return (
        '<div class="ur-equip">EQUIPAMENTO</div>'
        f'<div class="ur-equip-itens">{itens or "<span>Nenhum cadastrado</span>"}</div>'
    )


def faixa_situacao(espaco_id, reservas):
    """Texto e cor da faixa no topo do card, como no protótipo."""
    if reservas is None:
        return "Disponibilidade desconhecida", "cinza", False
    situacao, _, cor, detalhe = situacao_sala(espaco_id, reservas)
    if situacao == "Ocupada":
        return f"Ocupado {detalhe}", "vermelho", True
    if situacao == "Pré-reservada":
        return f"Pré-reservado {detalhe.split(' · ')[-1]}", "laranja", True
    if situacao == "Bloqueada":
        return "Bloqueado", "cinza", True
    return "Disponível agora", "verde", False


def card_sala(espaco, reservas, chave, ao_reservar=None, equipamentos=None,
              ao_editar=None, motivo_sem_reserva=None):
    """Card de sala: faixa de situação, dados da sala e botão Reservar."""
    eid = espaco["id"]
    texto_faixa, cor_faixa, ocupada = faixa_situacao(eid, reservas)
    localizacao = espaco.get("localizacao") or {}
    bloco = localizacao.get("bloco")
    nome = espaco.get("nome", "Sem nome")
    if bloco and f"bloco {bloco}".lower() not in nome.lower():
        nome = f"{nome}, Bloco {bloco}"

    with st.container(key=f"sala_{chave}_{eid}", gap=None):
        with st.container(key=f"faixa_{cor_faixa}_{chave}_{eid}"):
            st.markdown(f"●&nbsp; {texto_faixa}")
        with st.container(key=f"corpo_{chave}_{eid}"):
            # HTML em vez de st.markdown("####"): o título em markdown tem
            # margem negativa e cobria a linha de baixo quando não há andar.
            andar = localizacao.get("andar")
            st.html(
                f'<div class="ur-sala-titulo"><strong>{escape(nome)}</strong>'
                + (f'<span>Andar {escape(str(andar))}</span>' if andar else "")
                + "</div>"
            )
            detalhes = [f"Bloco {bloco}" if bloco else tipo_espaco(espaco.get("tipo"))[0]]
            if localizacao.get("identificacao"):
                detalhes.append(localizacao["identificacao"])
            st.caption(
                f"{' · '.join(detalhes)}  \n"
                f"Capacidade: {espaco.get('capacidade', '—')} lugares"
            )
            itens = nomes_equipamentos(espaco, equipamentos or {}) + list(
                espaco.get("caracteristicas") or []
            )
            st.html(_equipamentos_html(itens))
            st.space("xsmall")

            if ao_reservar:
                if st.button(
                    "Reservar",
                    type="primary",
                    key=f"reservar_{'ocupada' if ocupada else 'livre'}_{chave}_{eid}",
                    width="stretch",
                ):
                    ao_reservar(espaco)
            elif motivo_sem_reserva:
                st.button(
                    motivo_sem_reserva,
                    key=f"sem_reserva_{chave}_{eid}",
                    width="stretch",
                    disabled=True,
                )
            with st.container(horizontal=True, gap="small", horizontal_alignment="center"):
                if st.button(
                    "Ver agenda",
                    icon=":material/calendar_month:",
                    type="tertiary",
                    key=f"agenda_{chave}_{eid}",
                ):
                    ir_para("calendario", agenda_espaco_id=eid)
                if ao_editar and st.button(
                    "Editar",
                    icon=":material/edit:",
                    type="tertiary",
                    key=f"editar_{chave}_{eid}",
                ):
                    ao_editar(espaco)


def grade_salas(espacos, reservas, chave, colunas=4, **opcoes):
    """Grade de cards. ``opcoes`` repassa ao_reservar/ao_editar/etc. ao card.

    ``ao_reservar`` pode ser uma função que recebe o espaço e devolve o
    callback (ou None), para liberar a reserva só em algumas salas.
    """
    ao_reservar = opcoes.pop("ao_reservar", None)
    motivo = opcoes.pop("motivo_sem_reserva", None)
    for inicio in range(0, len(espacos), colunas):
        linha = st.columns(colunas, gap="medium")
        for coluna, espaco in zip(linha, espacos[inicio:inicio + colunas]):
            callback = ao_reservar(espaco) if callable(ao_reservar) else None
            with coluna:
                card_sala(
                    espaco, reservas, chave,
                    ao_reservar=callback,
                    motivo_sem_reserva=None if callback else motivo,
                    **opcoes,
                )


# ---------------------------------------------------------------------------
# Barra superior (todas as páginas)

def barra_superior(usuario, perfil, pagina_perfil):
    nome = usuario.get("nome") or "Usuário"
    nome_html = escape(nome)
    with st.container(key="topo", horizontal=True, vertical_alignment="center"):
        st.html(
            f'<div class="ur-topo-texto"><small>Bem-vindo,</small><strong class="grande">{nome_html}</strong></div>',
            width="stretch",
        )
        st.html(
            f'<div class="ur-topo-texto direita"><strong>{nome_html}</strong>'
            f'<small>Perfil: {escape(rotulo_perfil(perfil))}</small></div>',
            width="content",
        )
        if st.button(iniciais(nome), key="topo_avatar", help="Meu perfil"):
            st.switch_page(pagina_perfil)
