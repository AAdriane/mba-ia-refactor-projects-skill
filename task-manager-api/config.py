import os


class Config:
    """Configuração central lida de variáveis de ambiente. Nenhum segredo
    real vive aqui — apenas defaults seguros para desenvolvimento local.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "dev@example.com")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
