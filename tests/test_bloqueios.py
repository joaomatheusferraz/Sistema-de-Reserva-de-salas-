"""Testes de bloqueios administrativos (RF36, RN17, RN18, RN31)."""

import unittest
from datetime import datetime
from unittest.mock import patch

from controllers.bloqueio_controller import BloqueioController
from services.bloqueio_service import BloqueioService


class ModeloBloqueioFake:

    def __init__(self):
        self.criados = []

    def criar(self, dados):
        self.criados.append(dados)
        return "b1"

    def listar(self, apenas_ativos=True):
        return []

    def remover(self, bloqueio_id):
        return None


class ModeloEspacoFake:

    def buscar(self, espaco_id):
        return {"id": espaco_id, "ativo": True}


class HistoricoFake:

    def __init__(self):
        self.eventos = []

    def registrar(self, *args, **kwargs):
        self.eventos.append((args, kwargs))
        return "h1"


class ModeloReservaFake:
    """Devolve reservas ativas (pendentes e confirmadas) para checar conflitos."""

    def __init__(self, reservas):
        self.reservas = reservas

    def listar_ativas(self):
        return self.reservas


def reserva(id_, espaco_id, ini_h, fim_h, status="reservada"):
    return {
        "id": id_,
        "espaco_id": espaco_id,
        "inicio": datetime(2027, 3, 10, ini_h, 0),
        "fim": datetime(2027, 3, 10, fim_h, 0),
        "status": status,
    }


class BloqueioRN18Tests(unittest.TestCase):

    def setUp(self):
        self.modelo = ModeloBloqueioFake()
        self.historico = HistoricoFake()
        self.inicio = datetime(2027, 3, 10, 9, 0)
        self.fim = datetime(2027, 3, 10, 12, 0)

    def servico(self, reservas):
        return BloqueioService(
            self.modelo,
            ModeloEspacoFake(),
            self.historico,
            reserva_model=ModeloReservaFake(reservas),
        )

    def test_bloqueio_registra_ids_das_reservas_conflitantes(self):
        servico = self.servico([
            reserva("r1", "e1", 8, 10),
            reserva("r2", "e1", 11, 13, status="pendente"),
            reserva("r3", "e1", 14, 16),
            reserva("r4", "e2", 9, 12),
        ])
        servico.criar("e1", self.inicio, self.fim, "Manutenção", "coord1", "coordenador")
        self.assertEqual(self.modelo.criados[0]["reservas_conflitantes_ids"], ["r1", "r2"])

    def test_historico_do_bloqueio_informa_total_de_conflitos(self):
        servico = self.servico([reserva("r1", "e1", 9, 11)])
        servico.criar("e1", self.inicio, self.fim, "Evento", "coord1", "coordenador")
        _, kwargs = self.historico.eventos[0]
        self.assertEqual(kwargs["dados_novos"]["total_conflitos"], 1)

    def test_reserva_adjacente_nao_conflita_com_bloqueio(self):
        servico = self.servico([reserva("r1", "e1", 7, 9), reserva("r2", "e1", 12, 14)])
        conflitos = servico.verificar_reservas_conflitantes("e1", self.inicio, self.fim)
        self.assertEqual(conflitos, [])

    def test_bloqueio_sem_reservas_nao_gera_conflitos(self):
        servico = self.servico([])
        servico.criar("e1", self.inicio, self.fim, "Manutenção", "coord1", "coordenador")
        self.assertEqual(self.modelo.criados[0]["reservas_conflitantes_ids"], [])

    def test_bloqueio_exige_fim_posterior_ao_inicio(self):
        servico = self.servico([])
        with self.assertRaises(ValueError):
            servico.criar("e1", self.fim, self.inicio, "Manutenção", "coord1", "coordenador")

    def test_bloqueio_exige_motivo(self):
        servico = self.servico([])
        with self.assertRaises(ValueError):
            servico.criar("e1", self.inicio, self.fim, "  ", "coord1", "coordenador")

    def test_somente_coordenador_cria_bloqueio_rn05(self):
        servico = self.servico([])
        for perfil in ("aluno", "professor", "externo"):
            with self.assertRaises(PermissionError):
                servico.criar("e1", self.inicio, self.fim, "Manutenção", "u1", perfil)
        self.assertEqual(self.modelo.criados, [])

    def test_controller_padrao_recebe_modelo_de_reservas(self):
        """Sem o modelo de reservas, o aviso de RN18 nunca seria calculado."""
        reservas_fake = ModeloReservaFake([reserva("r1", "e1", 9, 11)])
        with patch("controllers.bloqueio_controller.ReservaModel", return_value=reservas_fake), \
                patch("services.bloqueio_service.BloqueioModel", return_value=self.modelo), \
                patch("services.bloqueio_service.EspacoModel", return_value=ModeloEspacoFake()), \
                patch("services.bloqueio_service.HistoricoService", return_value=self.historico):
            controller = BloqueioController()
            ok, _ = controller.criar_bloqueio(
                espaco_id="e1",
                inicio=self.inicio,
                fim=self.fim,
                motivo="Manutenção",
                responsavel_id="coord1",
                perfil="coordenador",
            )
        self.assertTrue(ok)
        self.assertEqual(self.modelo.criados[0]["reservas_conflitantes_ids"], ["r1"])


if __name__ == "__main__":
    unittest.main()
