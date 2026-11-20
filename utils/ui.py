"""Componentes visuais compartilhados entre as telas do UniReserve."""

from datetime import date, datetime, time, timedelta, timezone

import streamlit as st


# Horário de Brasília (sem horário de verão desde 2019).
FUSO_LOCAL = timezone(timedelta(hours=-3), "BRT")


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


def agora():
    return datetime.now(FUSO_LOCAL)


def para_local(valor):
    """Converte datetimes do Firestore (UTC) para o horário de Brasília."""
    if not isinstance(valor, datetime):
        return valor
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(FUSO_LOCAL)


def combinar_local(dia: date, horario: time):
    """Data + hora escolhidas na tela, já no horário de Brasília."""
    return datetime.combine(dia, horario, tzinfo=FUSO_LOCAL)


def formatar_data(valor, com_dia_semana=False):
    if not isinstance(valor, datetime):
        return str(valor or "—")
    valor = para_local(valor)
    texto = valor.strftime("%d/%m/%Y")
    if com_dia_semana:
        texto = f"{DIAS_SEMANA[valor.weekday()]}, {texto}"
    return texto


def formatar_hora(valor):
    if not isinstance(valor, datetime):
        return "—"
    return para_local(valor).strftime("%H:%M")


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


# ---------------------------------------------------------------------------
# Navegação: main.py registra as páginas disponíveis para o perfil atual.

def registrar_paginas(paginas):
    st.session_state["_paginas"] = paginas


def ir_para(nome, **estado):
    """Guarda valores na sessão (ex.: sala pré-selecionada) e troca de página."""
    st.session_state.update(estado)
    pagina = st.session_state.get("_paginas", {}).get(nome)
    if pagina is not None:
        st.switch_page(pagina)


def pagina_disponivel(nome):
    return nome in st.session_state.get("_paginas", {})


# ---------------------------------------------------------------------------
# Ocupação das salas

def situacao_sala(espaco_id, reservas, momento=None):
    """Retorna (rotulo, icone, cor, detalhe) da sala no momento informado."""
    momento = momento or agora()
    da_sala = sorted(
        (r for r in reservas if r.get("espaco_id") == espaco_id
         and isinstance(r.get("inicio"), datetime)),
        key=lambda r: r["inicio"],
    )
    for reserva in da_sala:
        if para_local(reserva["inicio"]) <= momento < para_local(reserva["fim"]):
            fim = formatar_hora(reserva["fim"])
            if reserva.get("status") == "reservada":
                return "Ocupada", ":material/do_not_disturb_on:", "red", f"até {fim}"
            return "Pré-reservada", ":material/schedule:", "orange", f"aguardando aprovação · até {fim}"
    proximas = [r for r in da_sala if para_local(r["inicio"]) > momento]
    if proximas and para_local(proximas[0]["inicio"]).date() == momento.date():
        return "Livre agora", ":material/check_circle:", "green", f"próxima reserva às {formatar_hora(proximas[0]['inicio'])}"
    return "Livre agora", ":material/check_circle:", "green", "sem reservas pelo resto do dia"


def reservas_do_dia(espaco_id, reservas, dia):
    return sorted(
        (r for r in reservas if r.get("espaco_id") == espaco_id
         and isinstance(r.get("inicio"), datetime)
         and para_local(r["inicio"]).date() == dia),
        key=lambda r: r["inicio"],
    )
