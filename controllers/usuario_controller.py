"""Controlador de gerenciamento de usuários e permissões."""

from domain.enums import Perfil
from services.usuario_service import UsuarioService


class UsuarioController:
    """Gerencia cadastro, consulta, atualização cadastral e permissões de usuários."""

    def __init__(self, service=None):
        self.service = service or UsuarioService()

    def cadastrar_usuario(self, nome, email, ra=None, perfil=Perfil.ALUNO.value):
        """Cadastra um novo usuário no sistema."""
        try:
            usuario_id = self.service.cadastrar(nome, email, ra, perfil)
            return True, f"Usuário cadastrado! ID: {usuario_id}"
        except (ValueError, TypeError) as erro:
            return False, str(erro)
        except Exception as erro:
            return False, f"Erro ao cadastrar usuário: {erro}"

    def listar_usuarios(self, apenas_ativos=False):
        """Lista usuários cadastrados, com opção de filtrar apenas ativos."""
        try:
            return self.service.listar(apenas_ativos=apenas_ativos)
        except Exception:
            return []

    def buscar_usuario(self, usuario_id):
        """Busca um usuário específico pelo ID."""
        try:
            usuario = self.service.buscar_por_id(usuario_id)
            if not usuario:
                return False, "Usuário não encontrado."
            return True, usuario
        except Exception as erro:
            return False, str(erro)

    def atualizar_usuario(
        self,
        usuario_id,
        nome,
        email,
        ra=None,
        perfil=Perfil.ALUNO.value,
        ativo=True,
    ):
        """Atualiza dados cadastrais, perfil de acesso e status de ativação."""
        try:
            self.service.atualizar(
                usuario_id,
                nome,
                email,
                ra,
                perfil,
                ativo,
            )
            return True, "Usuário atualizado com sucesso!"
        except (ValueError, TypeError) as erro:
            return False, str(erro)
        except Exception as erro:
            return False, f"Erro ao atualizar usuário: {erro}"

    def atualizar_contato(self, usuario, email, telefone):
        """Atualiza as informações de contato (e-mail e telefone) do próprio usuário."""
        try:
            self.service.atualizar_contato(
                usuario["id"],
                email,
                telefone,
                usuario.get("email"),
            )
            return True, "Dados de contato atualizados."
        except (ValueError, TypeError) as erro:
            return False, str(erro)
        except Exception as erro:
            mensagem = str(erro)
            if "EMAIL_EXISTS" in mensagem or "already exists" in mensagem:
                return False, "Este e-mail já está em uso por outra conta."
            return False, f"Não foi possível atualizar os dados: {erro}"

    def atualizar_autorizacoes(self, usuario_id, espacos_ids):
        """Atualiza a lista de espaços autorizados para usuários externos."""
        try:
            self.service.atualizar_autorizacoes(usuario_id, espacos_ids)
            return True, "Espaços autorizados atualizados!"
        except (ValueError, TypeError) as erro:
            return False, str(erro)
        except Exception as erro:
            return False, f"Erro ao salvar autorizações: {erro}"

    def excluir_usuario(self, usuario_id):
        """Remove um registro de usuário do sistema."""
        try:
            self.service.excluir(usuario_id)
            return True, "Usuário excluído com sucesso!"
        except (ValueError, TypeError) as erro:
            return False, str(erro)
        except Exception as erro:
            return False, f"Erro ao excluir usuário: {erro}"
