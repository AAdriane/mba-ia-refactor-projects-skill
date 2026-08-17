from database import db
from errors import NotFoundError, ValidationError
from models.category import Category
from models.task import Task


class CategoryService:
    def list_categories(self):
        # Agregação em uma única query em vez de contar tasks por
        # categoria dentro de um loop.
        counts = dict(
            db.session.query(Task.category_id, db.func.count(Task.id))
            .group_by(Task.category_id)
            .all()
        )
        return [
            {**category.to_dict(), 'task_count': counts.get(category.id, 0)}
            for category in Category.query.all()
        ]

    def create_category(self, data):
        if not data:
            raise ValidationError('Dados inválidos')
        name = data.get('name')
        if not name:
            raise ValidationError('Nome é obrigatório')

        category = Category()
        category.name = name
        category.description = data.get('description', '')
        category.color = data.get('color', '#000000')

        db.session.add(category)
        db.session.commit()
        return category

    def update_category(self, category_id, data):
        category = Category.query.get(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        if not data:
            raise ValidationError('Dados inválidos')

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            category.color = data['color']

        db.session.commit()
        return category

    def delete_category(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        db.session.delete(category)
        db.session.commit()
