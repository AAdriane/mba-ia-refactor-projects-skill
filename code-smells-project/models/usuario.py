from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db
from errors import ValidationError


class Usuario:
    """Entidade de domínio Usuario. Senha nunca é manipulada em texto puro."""

    def __init__(self, id=None, nome="", email="", senha_hash="", tipo="cliente", criado_em=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.tipo = tipo
        self.criado_em = criado_em

    @staticmethod
    def validar_cadastro(dados):
        erros = []
        if not dados.get("nome"):
            erros.append("Nome é obrigatório")
        if not dados.get("email"):
            erros.append("Email é obrigatório")
        if not dados.get("senha"):
            erros.append("Senha é obrigatória")
        if erros:
            raise ValidationError("; ".join(erros))

    def set_senha(self, senha_plana):
        self.senha_hash = generate_password_hash(senha_plana)

    def checar_senha(self, senha_plana):
        return check_password_hash(self.senha_hash, senha_plana)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tipo": self.tipo,
            "criado_em": self.criado_em,
        }

    @staticmethod
    def _from_row(row):
        return Usuario(
            id=row["id"], nome=row["nome"], email=row["email"],
            senha_hash=row["senha"], tipo=row["tipo"], criado_em=row["criado_em"],
        )


class UsuarioRepository:
    @staticmethod
    def get_all():
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM usuarios")
        return [Usuario._from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(id):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
        row = cursor.fetchone()
        return Usuario._from_row(row) if row else None

    @staticmethod
    def get_by_email(email):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        return Usuario._from_row(row) if row else None

    @staticmethod
    def create(usuario: Usuario):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (usuario.nome, usuario.email, usuario.senha_hash, usuario.tipo),
        )
        db.commit()
        return cursor.lastrowid
