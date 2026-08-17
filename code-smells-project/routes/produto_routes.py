from flask import Blueprint, request

from controllers.produto_controller import ProdutoController

produto_bp = Blueprint("produtos", __name__)


@produto_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    return ProdutoController.listar()


@produto_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)
    preco_min = float(preco_min) if preco_min else None
    preco_max = float(preco_max) if preco_max else None
    return ProdutoController.buscar(termo, categoria, preco_min, preco_max)


@produto_bp.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):
    return ProdutoController.buscar_por_id(id)


@produto_bp.route("/produtos", methods=["POST"])
def criar_produto():
    return ProdutoController.criar(request.get_json())


@produto_bp.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    return ProdutoController.atualizar(id, request.get_json())


@produto_bp.route("/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    return ProdutoController.deletar(id)
