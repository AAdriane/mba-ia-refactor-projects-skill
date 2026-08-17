from constants import MIN_PASSWORD_LENGTH, VALID_ROLES
from database import db
from errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError, ValidationError
from models.task import Task
from models.user import User
from services.auth_service import generate_token
from utils.helpers import validate_email


class UserService:
    def list_users(self):
        return User.query.all()

    def get_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        return user

    def create_user(self, data):
        if not data:
            raise ValidationError('Dados inválidos')

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not name:
            raise ValidationError('Nome é obrigatório')
        if not email:
            raise ValidationError('Email é obrigatório')
        if not password:
            raise ValidationError('Senha é obrigatória')
        if not validate_email(email):
            raise ValidationError('Email inválido')
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
        if User.query.filter_by(email=email).first():
            raise ConflictError('Email já cadastrado')
        if role not in VALID_ROLES:
            raise ValidationError('Role inválido')

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        db.session.add(user)
        db.session.commit()
        return user

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if not data:
            raise ValidationError('Dados inválidos')

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not validate_email(data['email']):
                raise ValidationError('Email inválido')
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < MIN_PASSWORD_LENGTH:
                raise ValidationError('Senha muito curta')
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in VALID_ROLES:
                raise ValidationError('Role inválido')
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        for task in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(task)
        db.session.delete(user)
        db.session.commit()

    def get_user_tasks(self, user_id):
        self.get_user(user_id)
        return Task.query.filter_by(user_id=user_id).all()

    def login(self, email, password):
        if not email or not password:
            raise ValidationError('Email e senha são obrigatórios')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise UnauthorizedError('Credenciais inválidas')
        if not user.active:
            raise ForbiddenError('Usuário inativo')

        token = generate_token(user.id)
        return user, token
