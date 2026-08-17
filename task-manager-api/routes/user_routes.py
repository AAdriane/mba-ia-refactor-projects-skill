from flask import Blueprint, request

from controllers.user_controller import UserController
from middlewares.auth import require_auth

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return UserController.list_users()


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return UserController.get_user(user_id)


@user_bp.route('/users', methods=['POST'])
def create_user():
    return UserController.create_user(request.get_json())


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    return UserController.update_user(user_id, request.get_json())


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    return UserController.delete_user(user_id)


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return UserController.get_user_tasks(user_id)


@user_bp.route('/login', methods=['POST'])
def login():
    return UserController.login(request.get_json())
