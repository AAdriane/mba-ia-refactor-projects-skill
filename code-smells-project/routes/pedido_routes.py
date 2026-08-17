from flask import Blueprint, request

from controllers.pedido_controller import PedidoController

pedido_bp = Blueprint("pedidos", __name__)


@pedido_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    return PedidoController.criar(request.get_json())


@pedido_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    return PedidoController.listar_todos()


@pedido_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    return PedidoController.listar_por_usuario(usuario_id)


@pedido_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    return PedidoController.atualizar_status(pedido_id, request.get_json())
