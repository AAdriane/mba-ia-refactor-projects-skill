from datetime import timedelta

from database import db
from errors import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import utcnow


class ReportService:
    def summary(self):
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        status_counts = dict(
            db.session.query(Task.status, db.func.count(Task.id)).group_by(Task.status).all()
        )
        priority_counts = dict(
            db.session.query(Task.priority, db.func.count(Task.id)).group_by(Task.priority).all()
        )

        overdue_list = [
            {
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (utcnow() - t.due_date).days,
            }
            for t in Task.query.all()
            if t.is_overdue()
        ]

        seven_days_ago = utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == 'done', Task.updated_at >= seven_days_ago
        ).count()

        # Substitui o loop "1 query por usuário" (finding MEDIUM
        # "N+1 Query Problem") por 2 queries agregadas totais.
        user_task_counts = dict(
            db.session.query(Task.user_id, db.func.count(Task.id)).group_by(Task.user_id).all()
        )
        user_done_counts = dict(
            db.session.query(Task.user_id, db.func.count(Task.id))
            .filter(Task.status == 'done')
            .group_by(Task.user_id)
            .all()
        )
        user_stats = []
        for user in User.query.all():
            total = user_task_counts.get(user.id, 0)
            completed = user_done_counts.get(user.id, 0)
            user_stats.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
            })

        return {
            'generated_at': str(utcnow()),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': total_users,
                'total_categories': total_categories,
            },
            'tasks_by_status': {
                'pending': status_counts.get('pending', 0),
                'in_progress': status_counts.get('in_progress', 0),
                'done': status_counts.get('done', 0),
                'cancelled': status_counts.get('cancelled', 0),
            },
            'tasks_by_priority': {
                'critical': priority_counts.get(1, 0),
                'high': priority_counts.get(2, 0),
                'medium': priority_counts.get(3, 0),
                'low': priority_counts.get(4, 0),
                'minimal': priority_counts.get(5, 0),
            },
            'overdue': {
                'count': len(overdue_list),
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        tasks = Task.query.filter_by(user_id=user_id).all()
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == 'done')
        pending = sum(1 for t in tasks if t.status == 'pending')
        in_progress = sum(1 for t in tasks if t.status == 'in_progress')
        cancelled = sum(1 for t in tasks if t.status == 'cancelled')
        high_priority = sum(1 for t in tasks if t.priority <= 2)
        overdue = sum(1 for t in tasks if t.is_overdue())

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': pending,
                'in_progress': in_progress,
                'cancelled': cancelled,
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
            },
        }
