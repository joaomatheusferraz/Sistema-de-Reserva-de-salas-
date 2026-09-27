import re


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validar_email(email):
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def texto_obrigatorio(valor):
    return isinstance(valor, str) and bool(valor.strip())
