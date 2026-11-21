import unittest

from utils.validators import texto_obrigatorio, validar_email


class TestValidators(unittest.TestCase):

    def test_validar_email_casos_validos(self):
        emails_validos = [
            "usuario@dominio.com",
            "aluno.silva@universidade.edu.br",
            "prof_matematica@faculdade.org",
            "teste+tag@empresa.com.br",
            "contato-123@sub.dominio.net",
        ]
        for email in emails_validos:
            with self.subTest(email=email):
                self.assertTrue(validar_email(email), f"Deveria aceitar: {email}")

    def test_validar_email_casos_invalidos(self):
        emails_invalidos = [
            "",
            "   ",
            None,
            12345,
            "usuario sem arroba.com",
            "@semusuario.com",
            "usuario@",
            "usuario@dominio",
            "usuario@dominio.",
            "usuario@.com",
            "usuario@dominio.c",  # TLD menor que 2 caracteres
            "usuario@@dominio.com",
            "usuario@dominio..com",
        ]
        for email in emails_invalidos:
            with self.subTest(email=email):
                self.assertFalse(validar_email(email), f"Deveria rejeitar: {email}")

    def test_texto_obrigatorio(self):
        self.assertTrue(texto_obrigatorio("texto válido"))
        self.assertTrue(texto_obrigatorio(" a "))
        self.assertFalse(texto_obrigatorio(""))
        self.assertFalse(texto_obrigatorio("   "))
        self.assertFalse(texto_obrigatorio(None))
        self.assertFalse(texto_obrigatorio(123))
        self.assertFalse(texto_obrigatorio([]))
        self.assertFalse(texto_obrigatorio({}))


if __name__ == "__main__":
    unittest.main()
