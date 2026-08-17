from flask import jsonify

from services.category_service import CategoryService

category_service = CategoryService()


class CategoryController:
    @staticmethod
    def list_categories():
        return jsonify(category_service.list_categories()), 200

    @staticmethod
    def create_category(data):
        category = category_service.create_category(data)
        return jsonify(category.to_dict()), 201

    @staticmethod
    def update_category(category_id, data):
        category = category_service.update_category(category_id, data)
        return jsonify(category.to_dict()), 200

    @staticmethod
    def delete_category(category_id):
        category_service.delete_category(category_id)
        return jsonify({'message': 'Categoria deletada'}), 200
