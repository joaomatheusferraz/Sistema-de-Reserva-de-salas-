"""Testes de horário de reserva: RN02, RN07 e RF19."""

import unittest
from datetime import datetime, timedelta

from test_services import (
    FakeHistory,
    FakeNotifications,
    FakeReservationModel,
    FakeSpaceModel,
    FakeUserModel,
)

from services.reserva_service import ReservaService
from utils.ui import FUSO_LOCAL


class HorarioReservaTests(unittest.TestCase):

    def setUp(self):
        amanha = datetime.now() + timedelta(days=1)
        self.dia = amanha.replace(hour=0, minute=0, second=0, microsecond=0)
        self.modelo = FakeReservationModel()

    def servico(self, perfil="professor"):
        return ReservaService(
            self.modelo,
            FakeUserModel(perfil),
            FakeSpaceModel(),
            FakeHistory(),
            FakeNotifications(),
        )

    def criar(self, ini_h, ini_m, fim_h, fim_m, perfil="professor"):
        return self.servico(perfil).criar(
            "e1",
            "u1",
            self.dia.replace(hour=ini_h, minute=ini_m),
            self.dia.replace(hour=fim_h, minute=fim_m),
            "Aula",
            perfil,
        )

    def test_rejeita_reserva_em_horario_ja_passado_rn07(self):
        ontem = (datetime.now() - timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        with self.assertRaises(ValueError) as ctx:
            self.servico().criar("e1", "u1", ontem, ontem + timedelta(hours=1), "Aula", "professor")
        self.assertIn("passou", str(ctx.exception))

    def test_coordenador_tambem_nao_reserva_no_passado_rn07(self):
        ontem = (datetime.now() - timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        with self.assertRaises(ValueError):
            self.servico("coordenador").criar(
                "e1", "u1", ontem, ontem + timedelta(hours=1), "Reunião", "coordenador"
            )

    def test_rejeita_reserva_no_passado_com_fuso_local_rn07(self):
        """A interface envia datetimes com fuso; a comparação não pode lançar TypeError."""
        ontem = (datetime.now(FUSO_LOCAL) - timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        with self.assertRaises(ValueError) as ctx:
            self.servico().criar("e1", "u1", ontem, ontem + timedelta(hours=1), "Aula", "professor")
        self.assertIn("passou", str(ctx.exception))

    def test_aceita_reserva_futura_com_fuso_local(self):
        amanha = (datetime.now(FUSO_LOCAL) + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        reserva_id = self.servico().criar(
            "e1", "u1", amanha, amanha + timedelta(hours=1), "Aula", "professor"
        )
        self.assertEqual(reserva_id, "r2")

    def test_rejeita_reserva_que_atravessa_a_meia_noite_rn07(self):
        inicio = self.dia.replace(hour=22)
        fim = (self.dia + timedelta(days=1)).replace(hour=6)
        with self.assertRaises(ValueError) as ctx:
            self.servico().criar("e1", "u1", inicio, fim, "Aula", "professor")
        self.assertIn("mesmo dia", str(ctx.exception))

    def test_aceita_reserva_nos_limites_do_funcionamento_rn07(self):
        self.assertEqual(self.criar(7, 0, 8, 0), "r2")
        self.assertEqual(self.criar(22, 0, 23, 0), "r2")
        self.assertEqual(self.criar(7, 0, 23, 0), "r2")

    def test_rejeita_reserva_fora_do_funcionamento_rn07(self):
        for ini, fim in (((6, 30), (8, 0)), ((22, 0), (23, 30))):
            with self.subTest(inicio=ini, fim=fim):
                with self.assertRaises(ValueError) as ctx:
                    self.criar(*ini, *fim)
                self.assertIn("07:00 e 23:00", str(ctx.exception))

    def test_rejeita_fim_igual_ou_anterior_ao_inicio_rf19(self):
        with self.assertRaises(ValueError):
            self.criar(10, 0, 10, 0)
        with self.assertRaises(ValueError):
            self.criar(11, 0, 10, 0)

    def test_rejeita_datas_sem_tipo_datetime_rf19(self):
        with self.assertRaises(ValueError):
            self.servico().criar("e1", "u1", "2027-01-01", "2027-01-02", "Aula", "professor")


if __name__ == "__main__":
    unittest.main()
