import re


EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
)


def validar_email(email):
    if not isinstance(email, str):
        return False
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def texto_obrigatorio(valor):
    return isinstance(valor, str) and bool(valor.strip())
