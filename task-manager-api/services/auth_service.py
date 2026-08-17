from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import Config

TOKEN_MAX_AGE_SECONDS = 60 * 60 * 8  # 8h


def _serializer():
    return URLSafeTimedSerializer(Config.SECRET_KEY, salt="auth-token")


def generate_token(user_id):
    """Substitui o token estático 'fake-jwt-token-<id>' (finding CRITICAL
    "Unauthenticated Sensitive/Destructive Endpoint") por um token assinado
    e com expiração, usando itsdangerous (já é dependência do Flask, sem
    precisar adicionar um novo pacote)."""
    return _serializer().dumps({"user_id": user_id})


def verify_token(token):
    try:
        data = _serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None
