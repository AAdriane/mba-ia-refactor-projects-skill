import os


class Config:
    """Configuração central da aplicação, lida de variáveis de ambiente.

    Nenhum segredo real vive aqui — apenas defaults seguros para
    desenvolvimento local. Em produção, todas essas variáveis devem ser
    definidas no ambiente (ou em um .env não versionado, ver .env.example).
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
