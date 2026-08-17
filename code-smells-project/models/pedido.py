from constants import STATUS_PEDIDO_VALIDOS
from database import get_db
from errors import NotFoundError, ValidationError
from models.produto import ProdutoRepository


class ItemPedido:
    def __init__(self, produto_id, quantidade, preco_unitario=None, produto_nome=None):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.produto_nome = produto_nome

    def to_dict(self):
        return {
            "produto_id": self.produto_id,
            "produto_nome": self.produto_nome,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
        }


class Pedido:
    def __init__(self, id=None, usuario_id=None, status="pendente", total=0, criado_em=None, itens=None):
        self.id = id
        self.usuario_id = usuario_id
        self.status = status
        self.total = total
        self.criado_em = criado_em
        self.itens = itens or []

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "status": self.status,
            "total": self.total,
            "criado_em": self.criado_em,
            "itens": [item.to_dict() for item in self.itens],
        }

    @staticmethod
    def validar_status(status):
        if status not in STATUS_PEDIDO_VALIDOS:
            raise ValidationError("Status inválido")


class PedidoRepository:
    @staticmethod
    def criar(usuario_id, itens_payload):
        """Cria pedido + itens + baixa de estoque em uma única transação.

        Corrige o finding MEDIUM "Missing Transactional Atomicity": qualquer
        exceção durante o processo reverte todas as escritas parciais.
        """
        if not itens_payload:
            raise ValidationError("Pedido deve ter pelo menos 1 item")

        db = get_db()
        cursor = db.cursor()
        try:
            total = 0
            produtos_por_id = {}
            for item in itens_payload:
                produto = ProdutoRepository.get_by_id(item["produto_id"])
                if produto is None:
                    raise NotFoundError(f"Produto {item['produto_id']} não encontrado")
                if produto.estoque < item["quantidade"]:
                    raise ValidationError(f"Estoque insuficiente para {produto.nome}")
                produtos_por_id[item["produto_id"]] = produto
                total += produto.preco * item["quantidade"]

            cursor.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                (usuario_id, total),
            )
            pedido_id = cursor.lastrowid

            for item in itens_payload:
                produto = produtos_por_id[item["produto_id"]]
                cursor.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                    "VALUES (?, ?, ?, ?)",
                    (pedido_id, item["produto_id"], item["quantidade"], produto.preco),
                )
                ProdutoRepository.decrementar_estoque(item["produto_id"], item["quantidade"], cursor)

            db.commit()
            return {"pedido_id": pedido_id, "total": total}
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _montar_pedidos(rows):
        """Monta pedidos + itens com uma única query em lote (corrige N+1)."""
        pedidos = [
            Pedido(id=row["id"], usuario_id=row["usuario_id"], status=row["status"],
                   total=row["total"], criado_em=row["criado_em"])
            for row in rows
        ]
        if not pedidos:
            return pedidos

        ids = [pedido.id for pedido in pedidos]
        placeholders = ",".join("?" for _ in ids)
        cursor = get_db().cursor()
        cursor.execute(
            f"""
            SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
            FROM itens_pedido ip
            JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id IN ({placeholders})
            """,
            ids,
        )

        itens_por_pedido = {}
        for row in cursor.fetchall():
            itens_por_pedido.setdefault(row["pedido_id"], []).append(
                ItemPedido(
                    produto_id=row["produto_id"], quantidade=row["quantidade"],
                    preco_unitario=row["preco_unitario"], produto_nome=row["produto_nome"],
                )
            )

        for pedido in pedidos:
            pedido.itens = itens_por_pedido.get(pedido.id, [])
        return pedidos

    @staticmethod
    def get_por_usuario(usuario_id):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        return PedidoRepository._montar_pedidos(cursor.fetchall())

    @staticmethod
    def get_todos():
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM pedidos")
        return PedidoRepository._montar_pedidos(cursor.fetchall())

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        Pedido.validar_status(novo_status)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        db.commit()

    @staticmethod
    def relatorio_vendas():
        cursor = get_db().cursor()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0]

        desconto = 0
        if faturamento > 10000:
            desconto = faturamento * 0.1
        elif faturamento > 5000:
            desconto = faturamento * 0.05
        elif faturamento > 1000:
            desconto = faturamento * 0.02

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
