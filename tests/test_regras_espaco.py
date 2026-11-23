"""Exibição das regras específicas do espaço antes de reservar (RN13, RF46)."""

import unittest

from views.reserva_dialogos import regras_do_espaco


class RegrasDoEspacoTests(unittest.TestCase):

    def test_retorna_regras_cadastradas_rn13(self):
        espaco = {"regras_especificas": ["Proibido alimentos", "Usar jaleco"]}
        self.assertEqual(regras_do_espaco(espaco), ["Proibido alimentos", "Usar jaleco"])

    def test_ignora_linhas_vazias_e_remove_espacos_rn13(self):
        espaco = {"regras_especificas": ["  Usar jaleco  ", "", "   ", None]}
        self.assertEqual(regras_do_espaco(espaco), ["Usar jaleco"])

    def test_espaco_sem_regras_nao_exibe_painel_rf46(self):
        self.assertEqual(regras_do_espaco({}), [])
        self.assertEqual(regras_do_espaco({"regras_especificas": None}), [])
        self.assertEqual(regras_do_espaco({"regras_especificas": []}), [])


if __name__ == "__main__":
    unittest.main()
