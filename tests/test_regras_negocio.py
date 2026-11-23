"""Testes baseados nas regras de negócio (RN) e requisitos funcionais (RF) do relatório final.

Cada teste cita a RN/RF que verifica, para facilitar a rastreabilidade com
docs/matriz_rastreabilidade.md e docs/criterios_aceitacao.md.
"""

import unittest
from datetime import datetime, timedelta

from test_services import (
    FakeHistory,
    FakeNotifications,
    FakeReservationModel,
    FakeSpaceModel,
    FakeUserModel,
)

from domain.enums import STATUS_OCUPAM_AGENDA, StatusReserva
from services.reserva_service import ReservaService


class EspacoInativoFake(FakeSpaceModel):

    def buscar(self, espaco_id):
        return {"id": espaco_id, "ativo": False}


class UsuarioInativoFake(FakeUserModel):

    def buscar(self, usuario_id):
        return {**super().buscar(usuario_id), "ativo": False}


class UsuarioInexistenteFake(FakeUserModel):

    def buscar(self, usuario_id):
        return None


class RegrasDeNegocioBase(unittest.TestCase):

    def setUp(self):
        self.inicio = (datetime.now() + timedelta(days=1)).replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        self.fim = self.inicio + timedelta(hours=2)
        self.modelo = FakeReservationModel()
        self.historico = FakeHistory()
        self.notificacoes = FakeNotifications()

    def servico(self, perfil="professor", autorizados=None, espaco_model=None, usuario_model=None):
        return ReservaService(
            self.modelo,
            usuario_model or FakeUserModel(perfil, autorizados),
            espaco_model or FakeSpaceModel(),
            self.historico,
            self.notificacoes,
        )

    def dados_edicao(self, **extra):
        return {
            "espaco_id": "e1",
            "inicio": self.inicio,
            "fim": self.fim,
            "finalidade": "Aula",
            **extra,
        }


class AgendaEStatusTests(RegrasDeNegocioBase):

    def test_apenas_pendente_e_reservada_ocupam_a_agenda_rn19_rn24(self):
        self.assertEqual(
            STATUS_OCUPAM_AGENDA,
            {StatusReserva.PENDENTE.value, StatusReserva.RESERVADA.value},
        )

    def test_cancelada_rejeitada_e_bloqueado_liberam_o_periodo_rn19(self):
        for status in (
            StatusReserva.CANCELADA.value,
            StatusReserva.REJEITADA.value,
            StatusReserva.BLOQUEADO.value,
        ):
            with self.subTest(status=status):
                self.assertNotIn(status, STATUS_OCUPAM_AGENDA)

    def test_solicitacao_pendente_ocupa_o_horario_rn24(self):
        self.assertIn(StatusReserva.PENDENTE.value, STATUS_OCUPAM_AGENDA)

    def test_cancelar_remove_a_reserva_da_agenda_rn19(self):
        servico = self.servico()
        servico.cancelar("r1", "u1", "professor")
        self.assertEqual(self.modelo.data["r1"]["status"], "cancelada")
        self.assertEqual(servico.listar_calendario(), [])

    def test_rejeitar_remove_a_solicitacao_da_agenda_rn19(self):
        servico = self.servico()
        servico.rejeitar("r1", "coord1", "coordenador", "Conflito de turma")
        self.assertEqual(self.modelo.data["r1"]["status"], "rejeitada")
        self.assertEqual(servico.listar_calendario(), [])


class FluxoDeAprovacaoTests(RegrasDeNegocioBase):

    def test_professor_e_externo_geram_solicitacao_pendente_rn21_rn25(self):
        for perfil, autorizados in (("professor", None), ("externo", ["e1"])):
            with self.subTest(perfil=perfil):
                self.servico(perfil, autorizados).criar(
                    "e1", "u1", self.inicio, self.fim, "Aula", perfil
                )
                reserva = self.modelo.data["r2"]
                self.assertEqual(reserva["status"], "pendente")
                self.assertTrue(reserva["aprovacao_necessaria"])
                self.assertIsNone(reserva["analisada_por_id"])

    def test_pendente_nao_e_reserva_confirmada_rn22(self):
        self.servico().criar("e1", "u1", self.inicio, self.fim, "Aula", "professor")
        self.assertNotEqual(self.modelo.data["r2"]["status"], "reservada")

    def test_somente_coordenador_aprova_rn25(self):
        servico = self.servico()
        for perfil in ("aluno", "professor", "externo"):
            with self.subTest(perfil=perfil):
                with self.assertRaises(PermissionError):
                    servico.aprovar("r1", "u1", perfil)
        self.assertEqual(self.modelo.data["r1"]["status"], "pendente")

    def test_somente_coordenador_rejeita_rn25(self):
        servico = self.servico()
        for perfil in ("aluno", "professor", "externo"):
            with self.subTest(perfil=perfil):
                with self.assertRaises(PermissionError):
                    servico.rejeitar("r1", "u1", perfil, "Sem vaga")
        self.assertEqual(self.modelo.data["r1"]["status"], "pendente")

    def test_somente_coordenador_lista_pendentes_rf39(self):
        servico = self.servico()
        self.assertEqual(len(servico.listar_pendentes("coordenador")), 1)
        with self.assertRaises(PermissionError):
            servico.listar_pendentes("professor")

    def test_aprovacao_registra_historico_e_notifica_rn20_rn23(self):
        self.servico().aprovar("r1", "coord1", "coordenador")
        self.assertEqual(self.modelo.data["r1"]["status"], "reservada")
        self.assertEqual(self.historico.events[-1][0][2], "aprovacao")
        usuario_id, tipo, _, reserva_id = self.notificacoes.events[-1]
        self.assertEqual((usuario_id, tipo, reserva_id), ("u1", "reserva_aprovada", "r1"))

    def test_rejeicao_grava_motivo_historico_e_notificacao_rf39_rn20(self):
        self.servico().rejeitar("r1", "coord1", "coordenador", "  Sala em manutenção  ")
        self.assertEqual(self.modelo.data["r1"]["motivo_rejeicao"], "Sala em manutenção")
        self.assertEqual(self.historico.events[-1][0][2], "rejeicao")
        self.assertEqual(self.notificacoes.events[-1][1], "reserva_rejeitada")

    def test_rejeicao_sem_motivo_nao_altera_status_rf39(self):
        servico = self.servico()
        for motivo in (None, "", "   "):
            with self.subTest(motivo=motivo):
                with self.assertRaises(ValueError):
                    servico.rejeitar("r1", "coord1", "coordenador", motivo)
        self.assertEqual(self.modelo.data["r1"]["status"], "pendente")

    def test_apenas_pendentes_podem_ser_aprovadas_ou_rejeitadas_rn21(self):
        servico = self.servico()
        self.modelo.data["r1"]["status"] = "reservada"
        with self.assertRaises(ValueError):
            servico.aprovar("r1", "coord1", "coordenador")
        with self.assertRaises(ValueError):
            servico.rejeitar("r1", "coord1", "coordenador", "Motivo")

    def test_cancelamento_registra_historico_e_notifica_rf27_rn20(self):
        self.servico().cancelar("r1", "u1", "professor")
        self.assertEqual(self.historico.events[-1][0][2], "cancelamento")
        self.assertEqual(self.notificacoes.events[-1][1], "reserva_cancelada")

    def test_reserva_ja_cancelada_nao_pode_ser_cancelada_de_novo_rn11(self):
        servico = self.servico()
        servico.cancelar("r1", "u1", "professor")
        with self.assertRaises(ValueError):
            servico.cancelar("r1", "u1", "professor")

    def test_criacao_notifica_o_solicitante_rf25(self):
        self.servico().criar("e1", "u1", self.inicio, self.fim, "Aula", "professor")
        usuario_id, tipo, mensagem, _ = self.notificacoes.events[-1]
        self.assertEqual((usuario_id, tipo), ("u1", "reserva_criada"))
        self.assertIn("aprovação", mensagem)

    def test_edicao_notifica_alteracao_rf26(self):
        self.servico().editar("r1", "u1", "professor", self.dados_edicao())
        self.assertEqual(self.notificacoes.events[-1][1], "reserva_alterada")
        self.assertEqual(self.historico.events[-1][0][2], "alteracao")


class FinalidadeEResponsavelTests(RegrasDeNegocioBase):

    def test_finalidade_obrigatoria_na_criacao_rn27(self):
        servico = self.servico()
        for finalidade in (None, "", "   "):
            with self.subTest(finalidade=finalidade):
                with self.assertRaises(ValueError) as ctx:
                    servico.criar("e1", "u1", self.inicio, self.fim, finalidade, "professor")
                self.assertIn("finalidade", str(ctx.exception).lower())

    def test_finalidade_obrigatoria_na_edicao_rn27(self):
        with self.assertRaises(ValueError):
            self.servico().editar("r1", "u1", "professor", self.dados_edicao(finalidade="  "))

    def test_finalidade_e_salva_sem_espacos_extras_rn27(self):
        self.servico().criar("e1", "u1", self.inicio, self.fim, "  Aula de BD  ", "professor")
        self.assertEqual(self.modelo.data["r2"]["finalidade"], "Aula de BD")

    def test_reserva_fica_vinculada_ao_responsavel_rn15(self):
        self.servico().criar("e1", "u1", self.inicio, self.fim, "Aula", "professor")
        self.assertEqual(self.modelo.data["r2"]["responsavel_id"], "u1")

    def test_responsavel_obrigatorio_rn15(self):
        with self.assertRaises(ValueError):
            self.servico().criar("e1", "", self.inicio, self.fim, "Aula", "professor")

    def test_responsavel_inativo_ou_inexistente_nao_reserva_rn15(self):
        for modelo in (UsuarioInativoFake("professor"), UsuarioInexistenteFake()):
            with self.subTest(modelo=type(modelo).__name__):
                with self.assertRaises(ValueError):
                    self.servico(usuario_model=modelo).criar(
                        "e1", "u1", self.inicio, self.fim, "Aula", "professor"
                    )

    def test_perfil_informado_deve_corresponder_ao_do_usuario_rn01(self):
        """Impede um professor de se passar por coordenador para ter reserva direta."""
        servico = self.servico("professor")
        with self.assertRaises(ValueError):
            servico.criar("e1", "u1", self.inicio, self.fim, "Aula", "coordenador")

    def test_espaco_desativado_nao_recebe_reserva_rn17(self):
        servico = self.servico(espaco_model=EspacoInativoFake())
        with self.assertRaises(ValueError):
            servico.criar("e1", "u1", self.inicio, self.fim, "Aula", "professor")

    def test_perfil_invalido_e_rejeitado_rn01(self):
        with self.assertRaises(ValueError):
            self.servico().criar("e1", "u1", self.inicio, self.fim, "Aula", "visitante")


class ConsultaPorAlunosTests(RegrasDeNegocioBase):

    def test_aluno_consulta_calendario_rf53_rn30(self):
        self.assertEqual(len(self.servico("aluno").listar_calendario()), 1)

    def test_aluno_nao_cria_reserva_rf53_rn30(self):
        with self.assertRaises(PermissionError):
            self.servico("aluno").criar("e1", "u1", self.inicio, self.fim, "Estudo", "aluno")

    def test_aluno_nao_edita_reserva_de_outro_usuario_rn30(self):
        with self.assertRaises(PermissionError):
            self.servico("aluno").editar("r1", "aluno1", "aluno", self.dados_edicao())

    def test_aluno_nao_cancela_reserva_de_outro_usuario_rn30(self):
        with self.assertRaises(PermissionError):
            self.servico("aluno").cancelar("r1", "aluno1", "aluno")
        self.assertEqual(self.modelo.data["r1"]["status"], "pendente")

    def test_aluno_nao_lista_todas_as_reservas_rn30(self):
        with self.assertRaises(PermissionError):
            self.servico("aluno").listar_todas("aluno")

    def test_aluno_nao_ve_historico_administrativo_rn05(self):
        with self.assertRaises(PermissionError):
            self.servico("aluno").historico_da_reserva("r1", "aluno")


class PermissaoDeAlteracaoTests(RegrasDeNegocioBase):

    def test_outro_professor_nao_cancela_reserva_alheia_rn04(self):
        with self.assertRaises(PermissionError):
            self.servico().cancelar("r1", "u2", "professor")

    def test_outro_professor_nao_edita_reserva_alheia_rn04(self):
        with self.assertRaises(PermissionError):
            self.servico().editar("r1", "u2", "professor", self.dados_edicao())

    def test_coordenador_edita_reserva_ja_aprovada_rn04(self):
        self.modelo.data["r1"]["status"] = "reservada"
        self.servico("coordenador").editar("r1", "coord1", "coordenador", self.dados_edicao())
        self.assertEqual(self.modelo.data["r1"]["finalidade"], "Aula")

    def test_externo_nao_edita_para_espaco_nao_autorizado_rn28(self):
        servico = self.servico("externo", ["e1"])
        with self.assertRaises(PermissionError):
            servico.editar("r1", "u1", "externo", self.dados_edicao(espaco_id="e9"))

    def test_reserva_cancelada_nao_pode_ser_editada_rn04(self):
        self.modelo.data["r1"]["status"] = "cancelada"
        with self.assertRaises(ValueError):
            self.servico().editar("r1", "u1", "professor", self.dados_edicao())

    def test_cancelar_reserva_inexistente_falha(self):
        with self.assertRaises(ValueError):
            self.servico().cancelar("inexistente", "u1", "professor")


if __name__ == "__main__":
    unittest.main()
