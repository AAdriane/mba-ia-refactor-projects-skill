from flask import jsonify

from errors import ValidationError
from models.pedido import PedidoRepository
from services.pedido_service import PedidoService

pedido_service = PedidoService()


class PedidoController:
    @staticmethod
    def criar(dados):
        if not dados:
            raise ValidationError("Dados inválidos")

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            raise ValidationError("Usuario ID é obrigatório")

        resultado = pedido_service.criar_pedido(usuario_id, itens)
        return jsonify({
            "dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso",
        }), 201

    @staticmethod
    def listar_por_usuario(usuario_id):
        pedidos = PedidoRepository.get_por_usuario(usuario_id)
        return jsonify({"dados": [p.to_dict() for p in pedidos], "sucesso": True}), 200

    @staticmethod
    def listar_todos():
        pedidos = PedidoRepository.get_todos()
        return jsonify({"dados": [p.to_dict() for p in pedidos], "sucesso": True}), 200

    @staticmethod
    def atualizar_status(pedido_id, dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        novo_status = dados.get("status", "")
        pedido_service.atualizar_status(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

    @staticmethod
    def relatorio_vendas():
        relatorio = PedidoRepository.relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
