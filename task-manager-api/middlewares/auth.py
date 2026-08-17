from functools import wraps

from flask import request

from errors import UnauthorizedError
from services.auth_service import verify_token


def require_auth(f):
    """Protege rotas de escrita (POST/PUT/DELETE) exigindo um token válido
    obtido via /login. Corrige o finding CRITICAL "Unauthenticated
    Sensitive/Destructive Endpoint" — antes nenhuma rota validava o token
    retornado pelo login."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        user_id = verify_token(token) if token else None
        if not user_id:
            raise UnauthorizedError("Autenticação necessária")
        request.user_id = user_id
        return f(*args, **kwargs)

    return wrapper
