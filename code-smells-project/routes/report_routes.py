from flask import Blueprint

from controllers.pedido_controller import PedidoController

report_bp = Blueprint("relatorios", __name__)


@report_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    return PedidoController.relatorio_vendas()
