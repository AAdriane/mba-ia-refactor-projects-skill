from flask import Blueprint

from controllers.health_controller import HealthController

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    return HealthController.check()
