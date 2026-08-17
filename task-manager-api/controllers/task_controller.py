from flask import jsonify

from services.task_service import TaskService

task_service = TaskService()


class TaskController:
    @staticmethod
    def list_tasks():
        tasks = task_service.list_tasks()
        return jsonify([t.to_dict() for t in tasks]), 200

    @staticmethod
    def get_task(task_id):
        task = task_service.get_task(task_id)
        return jsonify(task.to_dict()), 200

    @staticmethod
    def search_tasks(query, status, priority, user_id):
        tasks = task_service.search_tasks(query, status, priority, user_id)
        return jsonify([t.to_dict() for t in tasks]), 200

    @staticmethod
    def create_task(data):
        task = task_service.create_task(data)
        return jsonify(task.to_dict()), 201

    @staticmethod
    def update_task(task_id, data):
        task = task_service.update_task(task_id, data)
        return jsonify(task.to_dict()), 200

    @staticmethod
    def delete_task(task_id):
        task_service.delete_task(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200

    @staticmethod
    def stats():
        return jsonify(task_service.stats()), 200
