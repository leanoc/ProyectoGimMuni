import datetime
import re
from config import MINIMUM_AGE

def validate_dni(dni: str) -> bool:
    """Valida que el DNI contenga exclusivamente entre 7 y 8 números."""
    return bool(re.fullmatch(r"\d{7,8}", dni.strip()))

def validate_date(date_text: str) -> bool:
    """Valida formato AAAA-MM-DD y que represente una fecha real del calendario."""
    try:
        parsed = datetime.datetime.strptime(date_text.strip(), "%Y-%m-%d").date()
        return parsed < datetime.date.today()
    except ValueError:
        return False

def validate_minimum_age(birth_date_str: str, min_age: int = MINIMUM_AGE) -> bool:
    """Calcula la edad exacta considerando si ya cumplió años en el año actual."""
    try:
        birth_date = datetime.datetime.strptime(birth_date_str.strip(), "%Y-%m-%d").date()
        today = datetime.date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age >= min_age
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    """Valida estructura general de correo electrónico."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.fullmatch(pattern, email.strip()))

def validate_not_empty(text: str) -> bool:
    """Verifica que el campo no esté vacío o compuesto solo por espacios."""
    return len(text.strip()) > 0