from flask import Blueprint, request

from controllers.category_controller import CategoryController
from controllers.report_controller import ReportController
from middlewares.auth import require_auth

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return ReportController.summary()


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return ReportController.user_report(user_id)


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return CategoryController.list_categories()


@report_bp.route('/categories', methods=['POST'])
@require_auth
def create_category():
    return CategoryController.create_category(request.get_json())


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@require_auth
def update_category(cat_id):
    return CategoryController.update_category(cat_id, request.get_json())


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@require_auth
def delete_category(cat_id):
    return CategoryController.delete_category(cat_id)
