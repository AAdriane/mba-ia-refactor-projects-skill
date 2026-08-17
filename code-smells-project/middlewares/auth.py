from functools import wraps

from flask import request

from config import Config
from errors import UnauthorizedError


def require_admin(f):
    """Protege rotas administrativas com um token estático via header.

    Corrige o finding CRITICAL "Unauthenticated Sensitive/Destructive
    Endpoint" — antes /admin/reset-db não exigia nenhuma verificação.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token")
        if not Config.ADMIN_TOKEN or token != Config.ADMIN_TOKEN:
            raise UnauthorizedError("Acesso administrativo negado")
        return f(*args, **kwargs)

    return wrapper
