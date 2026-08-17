from sqlalchemy.orm import joinedload

from database import db
from errors import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from services.notification_service import NotificationService
from utils.helpers import process_task_data


class TaskService:
    def __init__(self, notification_service: NotificationService = None):
        self.notification_service = notification_service or NotificationService()

    def list_tasks(self):
        # joinedload evita o N+1 de buscar user/category por task
        # (finding MEDIUM "N+1 Query Problem").
        return Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()

    def get_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise NotFoundError('Task não encontrada')
        return task

    def search_tasks(self, query=None, status=None, priority=None, user_id=None):
        tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category))
        if query:
            tasks = tasks.filter(
                db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
            )
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))
        return tasks.all()

    def create_task(self, data):
        if not data:
            raise ValidationError('Dados inválidos')

        # Reaproveita a validação central que já existia em utils/helpers.py
        # mas nunca era chamada (finding MEDIUM "Duplicated Validation").
        validated, error = process_task_data(data)
        if error:
            raise ValidationError(error)
        if 'title' not in validated:
            raise ValidationError('Título é obrigatório')

        user_id = data.get('user_id')
        category_id = data.get('category_id')
        if user_id and not User.query.get(user_id):
            raise NotFoundError('Usuário não encontrado')
        if category_id and not Category.query.get(category_id):
            raise NotFoundError('Categoria não encontrada')

        task = Task()
        task.title = validated['title']
        task.description = validated.get('description', data.get('description', ''))
        task.status = validated.get('status', 'pending')
        task.priority = validated.get('priority', 3)
        task.user_id = user_id
        task.category_id = category_id
        task.due_date = validated.get('due_date')
        if 'tags' in validated:
            task.tags = validated['tags']

        db.session.add(task)
        db.session.commit()

        # Finding HIGH "Fat Controller": NotificationService existia mas
        # nunca era chamado — agora é integrado ao criar uma task com
        # responsável.
        if task.user_id:
            user = User.query.get(task.user_id)
            self.notification_service.notify_task_assigned(user, task)

        return task

    def update_task(self, task_id, data):
        task = self.get_task(task_id)
        if not data:
            raise ValidationError('Dados inválidos')

        validated, error = process_task_data(data, existing_task=task)
        if error:
            raise ValidationError(error)

        if 'user_id' in data and data['user_id'] and not User.query.get(data['user_id']):
            raise NotFoundError('Usuário não encontrado')
        if 'category_id' in data and data['category_id'] and not Category.query.get(data['category_id']):
            raise NotFoundError('Categoria não encontrada')

        for field, value in validated.items():
            setattr(task, field, value)
        if 'user_id' in data:
            task.user_id = data['user_id']
        if 'category_id' in data:
            task.category_id = data['category_id']

        db.session.commit()
        return task

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        db.session.delete(task)
        db.session.commit()

    def stats(self):
        total = Task.query.count()
        status_counts = dict(
            db.session.query(Task.status, db.func.count(Task.id)).group_by(Task.status).all()
        )
        overdue = sum(1 for t in Task.query.all() if t.is_overdue())

        done = status_counts.get('done', 0)
        return {
            'total': total,
            'pending': status_counts.get('pending', 0),
            'in_progress': status_counts.get('in_progress', 0),
            'done': done,
            'cancelled': status_counts.get('cancelled', 0),
            'overdue': overdue,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }
