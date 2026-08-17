from flask import jsonify

from services.user_service import UserService

user_service = UserService()


class UserController:
    @staticmethod
    def list_users():
        users = user_service.list_users()
        result = []
        for user in users:
            data = user.to_dict()
            data['task_count'] = len(user.tasks)
            result.append(data)
        return jsonify(result), 200

    @staticmethod
    def get_user(user_id):
        user = user_service.get_user(user_id)
        data = user.to_dict()
        data['tasks'] = [t.to_dict() for t in user_service.get_user_tasks(user_id)]
        return jsonify(data), 200

    @staticmethod
    def create_user(data):
        user = user_service.create_user(data)
        return jsonify(user.to_dict()), 201

    @staticmethod
    def update_user(user_id, data):
        user = user_service.update_user(user_id, data)
        return jsonify(user.to_dict()), 200

    @staticmethod
    def delete_user(user_id):
        user_service.delete_user(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200

    @staticmethod
    def get_user_tasks(user_id):
        tasks = user_service.get_user_tasks(user_id)
        return jsonify([t.to_dict() for t in tasks]), 200

    @staticmethod
    def login(data):
        email = data.get('email') if data else None
        password = data.get('password') if data else None
        user, token = user_service.login(email, password)
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': token,
        }), 200
