import logging

from flask import jsonify

from errors import NotFoundError, ValidationError
from models.produto import Produto, ProdutoRepository

logger = logging.getLogger(__name__)


class ProdutoController:
    @staticmethod
    def listar():
        produtos = ProdutoRepository.get_all()
        logger.info("Listando %d produtos", len(produtos))
        return jsonify({"dados": [p.to_dict() for p in produtos], "sucesso": True}), 200

    @staticmethod
    def buscar_por_id(id):
        produto = ProdutoRepository.get_by_id(id)
        if not produto:
            raise NotFoundError("Produto não encontrado")
        return jsonify({"dados": produto.to_dict(), "sucesso": True}), 200

    @staticmethod
    def buscar(termo, categoria, preco_min, preco_max):
        resultados = ProdutoRepository.search(termo, categoria, preco_min, preco_max)
        dados = [p.to_dict() for p in resultados]
        return jsonify({"dados": dados, "total": len(dados), "sucesso": True}), 200

    @staticmethod
    def criar(dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        Produto.validar(dados)

        produto = Produto(
            nome=dados["nome"], descricao=dados.get("descricao", ""),
            preco=dados["preco"], estoque=dados["estoque"],
            categoria=dados.get("categoria", "geral"),
        )
        id = ProdutoRepository.create(produto)
        logger.info("Produto criado com ID %s", id)
        return jsonify({"dados": {"id": id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    @staticmethod
    def atualizar(id, dados):
        if not ProdutoRepository.get_by_id(id):
            raise NotFoundError("Produto não encontrado")
        if not dados:
            raise ValidationError("Dados inválidos")
        Produto.validar(dados)

        produto = Produto(
            nome=dados["nome"], descricao=dados.get("descricao", ""),
            preco=dados["preco"], estoque=dados["estoque"],
            categoria=dados.get("categoria", "geral"),
        )
        ProdutoRepository.update(id, produto)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    @staticmethod
    def deletar(id):
        if not ProdutoRepository.get_by_id(id):
            raise NotFoundError("Produto não encontrado")
        ProdutoRepository.delete(id)
        logger.info("Produto %s deletado", id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
