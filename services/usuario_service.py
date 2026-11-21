from domain.enums import Perfil
from models.usuario_model import UsuarioModel
from utils.validators import texto_obrigatorio, validar_email


class UsuarioService:

    def __init__(self, model=None):
        self.model = model or UsuarioModel()

    def cadastrar(self, nome, email, ra=None, perfil=Perfil.ALUNO.value, uid=None):
        nome = (nome or "").strip()
        email = (email or "").strip()
        ra = str(ra).strip() if (ra is not None and str(ra).strip()) else None

        if not texto_obrigatorio(nome):
            raise ValueError("Informe o nome.")
        if not texto_obrigatorio(email):
            raise ValueError("Informe o e-mail.")
        if not validar_email(email):
            raise ValueError("Informe um e-mail válido.")

        perfil_normalizado = str(perfil).strip().lower() if perfil is not None else ""
        if perfil_normalizado not in {item.value for item in Perfil}:
            raise ValueError("Perfil inválido.")

        if ra:
            usuario_existente = self.model.buscar_por_ra(ra)
            if usuario_existente and usuario_existente.get("id") != uid:
                raise ValueError("Já existe um usuário cadastrado com este RA.")

        return self.model.criar(nome, email, ra, perfil_normalizado, uid=uid)

    def listar(self, apenas_ativos=False):
        usuarios = self.model.listar()
        if apenas_ativos:
            return [u for u in usuarios if u.get("ativo", True)]
        return usuarios

    def buscar_por_id(self, usuario_id):
        if not texto_obrigatorio(usuario_id):
            raise ValueError("ID do usuário inválido.")
        return self.model.buscar(usuario_id)

    def buscar_por_ra(self, ra):
        if not ra:
            return None
        return self.model.buscar_por_ra(str(ra).strip())

    def atualizar(self, usuario_id, nome, email, ra=None, perfil=Perfil.ALUNO.value, ativo=True):
        if not texto_obrigatorio(usuario_id):
            raise ValueError("ID do usuário inválido.")

        nome = (nome or "").strip()
        email = (email or "").strip()
        ra = str(ra).strip() if (ra is not None and str(ra).strip()) else None

        if not texto_obrigatorio(nome):
            raise ValueError("Informe o nome.")
        if not texto_obrigatorio(email):
            raise ValueError("Informe o e-mail.")
        if not validar_email(email):
            raise ValueError("Informe um e-mail válido.")

        perfil_normalizado = str(perfil).strip().lower() if perfil is not None else ""
        if perfil_normalizado not in {item.value for item in Perfil}:
            raise ValueError("Perfil inválido.")

        if ra:
            usuario_existente = self.model.buscar_por_ra(ra)
            if usuario_existente and usuario_existente.get("id") != usuario_id:
                raise ValueError("Já existe outro usuário cadastrado com este RA.")

        self.model.atualizar(usuario_id, nome, email, ra, perfil_normalizado, ativo)

    def atualizar_contato(self, usuario_id, email, telefone, email_anterior=None):
        if not texto_obrigatorio(usuario_id):
            raise ValueError("ID do usuário inválido.")

        email = (email or "").strip()
        telefone = (telefone or "").strip()

        if not texto_obrigatorio(email):
            raise ValueError("Informe o e-mail.")
        if not validar_email(email):
            raise ValueError("Informe um e-mail válido.")
        if telefone and len("".join(c for c in telefone if c.isdigit())) < 10:
            raise ValueError("Informe o telefone com DDD.")

        self.model.atualizar_contato(usuario_id, email, telefone, email_anterior)

    def atualizar_autorizacoes(self, usuario_id, espacos_ids):
        if not texto_obrigatorio(usuario_id):
            raise ValueError("ID do usuário inválido.")
        if not isinstance(espacos_ids, (list, set, tuple)):
            raise TypeError("espacos_ids deve ser uma coleção de identificadores.")
        self.model.atualizar_autorizacoes(usuario_id, list(espacos_ids))

    def excluir(self, usuario_id):
        if not texto_obrigatorio(usuario_id):
            raise ValueError("ID do usuário inválido.")
        self.model.excluir(usuario_id)
