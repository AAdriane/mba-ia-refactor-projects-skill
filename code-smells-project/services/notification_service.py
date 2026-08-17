import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Simula o envio de notificações (email/SMS/push) via logging estruturado.

    Antes vivia como `print()` solto dentro do controller de pedidos —
    corrige o finding LOW "Unstructured Logging" nesse trecho e também
    remove efeito colateral de dentro do Controller (ver Fat Controller).
    """

    def notificar_pedido_criado(self, pedido_id, usuario_id):
        logger.info(
            "Notificando criação do pedido %s para usuário %s (email/sms/push)",
            pedido_id, usuario_id,
        )

    def notificar_status_pedido(self, pedido_id, novo_status):
        if novo_status == "aprovado":
            logger.info("Pedido %s aprovado — preparar envio", pedido_id)
        elif novo_status == "cancelado":
            logger.info("Pedido %s cancelado — devolver estoque", pedido_id)
