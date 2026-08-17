from flask import Blueprint

from controllers.admin_controller import AdminController
from middlewares.auth import require_admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/reset-db", methods=["POST"])
@require_admin
def reset_database():
    return AdminController.reset_database()
