import logging
import re
import uuid
from datetime import datetime, timezone

from constants import (
    MAX_TITLE_LENGTH,
    MAX_PRIORITY,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_STATUSES,
)

logger = logging.getLogger(__name__)


def utcnow():
    """Substitui datetime.utcnow() (deprecated desde o Python 3.12),
    mantendo o mesmo comportamento: datetime naive em UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email))


def sanitize_string(s):
    if s:
        return s.strip()
    return s


def generate_id():
    return str(uuid.uuid4())


def log_action(action, details=None):
    logger.info("ACTION: %s%s", action, f" | DETAILS: {details}" if details else "")


def parse_date(date_string):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None


def is_valid_color(color):
    return bool(color) and len(color) == 7 and color[0] == '#'


def process_task_data(data, existing_task=None):
    """Validação centralizada de payload de Task.

    Antes existia mas nunca era chamada pelas rotas (finding MEDIUM
    "Duplicated Validation / Business Logic") — agora é reutilizada por
    services/task_service.py em vez de a validação ser reimplementada.
    """
    result = {}

    if 'title' in data:
        title = data['title']
        if title:
            title = title.strip()
            if MIN_TITLE_LENGTH <= len(title) <= MAX_TITLE_LENGTH:
                result['title'] = title
            else:
                return None, f'Título deve ter entre {MIN_TITLE_LENGTH} e {MAX_TITLE_LENGTH} caracteres'
        else:
            return None, 'Título não pode ser vazio'

    if 'description' in data:
        result['description'] = data['description']

    if 'status' in data:
        if data['status'] in VALID_STATUSES:
            result['status'] = data['status']
        else:
            return None, 'Status inválido'

    if 'priority' in data:
        try:
            priority = int(data['priority'])
            if MIN_PRIORITY <= priority <= MAX_PRIORITY:
                result['priority'] = priority
            else:
                return None, f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}'
        except (TypeError, ValueError):
            return None, 'Prioridade inválida'

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if parsed:
                result['due_date'] = parsed
            else:
                return None, 'Data inválida'
        else:
            result['due_date'] = None

    if 'tags' in data:
        tags = data['tags']
        result['tags'] = ','.join(tags) if isinstance(tags, list) else tags

    return result, None
