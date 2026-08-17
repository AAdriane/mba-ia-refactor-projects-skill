from flask import Blueprint, request

from controllers.task_controller import TaskController
from middlewares.auth import require_auth

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return TaskController.list_tasks()


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    return TaskController.search_tasks(
        request.args.get('q', ''),
        request.args.get('status', ''),
        request.args.get('priority', ''),
        request.args.get('user_id', ''),
    )


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return TaskController.stats()


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return TaskController.get_task(task_id)


@task_bp.route('/tasks', methods=['POST'])
@require_auth
def create_task():
    return TaskController.create_task(request.get_json())


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@require_auth
def update_task(task_id):
    return TaskController.update_task(task_id, request.get_json())


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@require_auth
def delete_task(task_id):
    return TaskController.delete_task(task_id)
