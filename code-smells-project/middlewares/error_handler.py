import logging

from flask import jsonify

from errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Handler central de erro — nenhuma rota deve capturar `Exception` genérica."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"erro": str(error), "sucesso": False}), error.status_code

    @app.errorhandler(404)
    def handle_404(_error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
