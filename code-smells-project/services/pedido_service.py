from models.pedido import PedidoRepository
from services.notification_service import NotificationService


class PedidoService:
    """Orquestra o caso de uso de pedido, coordenando Model + notificações."""

    def __init__(self, notification_service: NotificationService = None):
        self.notification_service = notification_service or NotificationService()

    def criar_pedido(self, usuario_id, itens):
        resultado = PedidoRepository.criar(usuario_id, itens)
        self.notification_service.notificar_pedido_criado(resultado["pedido_id"], usuario_id)
        return resultado

    def atualizar_status(self, pedido_id, novo_status):
        PedidoRepository.atualizar_status(pedido_id, novo_status)
        self.notification_service.notificar_status_pedido(pedido_id, novo_status)
