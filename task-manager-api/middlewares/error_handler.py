import logging

from flask import jsonify

from errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Handler central de erro — substitui os `except:` genéricos
    espalhados pelas rotas (finding MEDIUM "Broad Exception Handling")."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": str(error)}), error.status_code

    @app.errorhandler(404)
    def handle_404(_error):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        logger.exception("Erro não tratado")
        return jsonify({"error": "Erro interno"}), 500
