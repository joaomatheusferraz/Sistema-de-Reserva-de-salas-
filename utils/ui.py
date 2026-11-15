"""Componentes visuais compartilhados entre as telas do UniReserve."""

from datetime import datetime

import streamlit as st


PERFIS = {
    "aluno": ("Aluno", ":material/school:", "blue"),
    "professor": ("Professor", ":material/co_present:", "violet"),
    "externo": ("Usuário externo", ":material/badge:", "gray"),
    "coordenador": ("Coordenador", ":material/admin_panel_settings:", "orange"),
}

STATUS = {
    "pendente": ("Pendente", ":material/schedule:", "orange"),
    "reservada": ("Confirmada", ":material/check_circle:", "green"),
    "rejeitada": ("Rejeitada", ":material/cancel:", "red"),
    "cancelada": ("Cancelada", ":material/block:", "gray"),
}

TIPOS_ESPACO = {
    "sala": ("Sala", ":material/meeting_room:"),
    "laboratorio": ("Laboratório", ":material/science:"),
}

DIAS_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def normalizar_perfil(usuario):
    return str((usuario or {}).get("perfil", "aluno")).strip().lower()


def perfil_badge(perfil):
    rotulo, icone, cor = PERFIS.get(perfil, (perfil.title(), ":material/person:", "gray"))
    st.badge(rotulo, icon=icone, color=cor)


def status_badge(status):
    rotulo, icone, cor = STATUS.get(status, (str(status).title(), ":material/help:", "gray"))
    st.badge(rotulo, icon=icone, color=cor)


def status_markdown(status):
    """Badge inline para usar dentro de textos e tabelas markdown."""
    rotulo, _, cor = STATUS.get(status, (str(status).title(), None, "gray"))
    return f":{cor}-badge[{rotulo}]"


def tipo_espaco(tipo):
    return TIPOS_ESPACO.get(tipo, (str(tipo).title(), ":material/location_city:"))


def formatar_data(valor, com_dia_semana=False):
    if not isinstance(valor, datetime):
        return str(valor or "—")
    texto = valor.strftime("%d/%m/%Y")
    if com_dia_semana:
        texto = f"{DIAS_SEMANA[valor.weekday()]}, {texto}"
    return texto


def formatar_hora(valor):
    if not isinstance(valor, datetime):
        return "—"
    return valor.strftime("%H:%M")


def formatar_periodo(inicio, fim):
    """Ex.: 'qua, 18/11/2026 · 08:00–09:30'."""
    if not isinstance(inicio, datetime):
        return "Período não informado"
    return (
        f"{formatar_data(inicio, com_dia_semana=True)} · "
        f"{formatar_hora(inicio)}–{formatar_hora(fim)}"
    )


def localizacao_texto(espaco):
    localizacao = espaco.get("localizacao") or {}
    partes = []
    if localizacao.get("bloco"):
        partes.append(f"Bloco {localizacao['bloco']}")
    if localizacao.get("identificacao"):
        partes.append(localizacao["identificacao"])
    return " · ".join(partes) or "Localização não informada"


def cabecalho(titulo, descricao=None, icone=None):
    st.title(titulo, icon=icone, anchor=False)
    if descricao:
        st.caption(descricao)


def estado_vazio(mensagem, icone=":material/inbox:"):
    with st.container(border=True, horizontal_alignment="center"):
        st.markdown(f"### {icone}", text_alignment="center")
        st.caption(mensagem, text_alignment="center")
