from constants import CATEGORIAS_VALIDAS
from database import get_db
from errors import ValidationError


class Produto:
    """Entidade de domínio Produto + regras de validação (invariantes)."""

    def __init__(self, id=None, nome="", descricao="", preco=0, estoque=0,
                 categoria="geral", ativo=1, criado_em=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.estoque = estoque
        self.categoria = categoria
        self.ativo = ativo
        self.criado_em = criado_em

    @staticmethod
    def validar(dados):
        erros = []

        nome = dados.get("nome")
        if not nome:
            erros.append("Nome é obrigatório")
        elif len(nome) < 2:
            erros.append("Nome muito curto")
        elif len(nome) > 200:
            erros.append("Nome muito longo")

        if dados.get("preco") is None:
            erros.append("Preço é obrigatório")
        elif dados["preco"] < 0:
            erros.append("Preço não pode ser negativo")

        if dados.get("estoque") is None:
            erros.append("Estoque é obrigatório")
        elif dados["estoque"] < 0:
            erros.append("Estoque não pode ser negativo")

        categoria = dados.get("categoria", "geral")
        if categoria not in CATEGORIAS_VALIDAS:
            erros.append("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

        if erros:
            raise ValidationError("; ".join(erros))

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "preco": self.preco,
            "estoque": self.estoque,
            "categoria": self.categoria,
            "ativo": self.ativo,
            "criado_em": self.criado_em,
        }

    @staticmethod
    def _from_row(row):
        return Produto(
            id=row["id"], nome=row["nome"], descricao=row["descricao"],
            preco=row["preco"], estoque=row["estoque"], categoria=row["categoria"],
            ativo=row["ativo"], criado_em=row["criado_em"],
        )


class ProdutoRepository:
    """Acesso a dados de Produto — toda query é parametrizada (sem SQL Injection)."""

    @staticmethod
    def get_all():
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM produtos")
        return [Produto._from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(id):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
        row = cursor.fetchone()
        return Produto._from_row(row) if row else None

    @staticmethod
    def create(produto: Produto):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (produto.nome, produto.descricao, produto.preco, produto.estoque, produto.categoria),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update(id, produto: Produto):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (produto.nome, produto.descricao, produto.preco, produto.estoque, produto.categoria, id),
        )
        db.commit()

    @staticmethod
    def delete(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
        db.commit()

    @staticmethod
    def search(termo=None, categoria=None, preco_min=None, preco_max=None):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            params += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)

        cursor = get_db().cursor()
        cursor.execute(query, params)
        return [Produto._from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def decrementar_estoque(produto_id, quantidade, cursor):
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id),
        )
