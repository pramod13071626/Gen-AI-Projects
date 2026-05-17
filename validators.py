import re


def validate_email(email):
    """Validate email format. Returns error message or None."""
    if not email:
        return "Email is required"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return "Invalid email format"
    return None


def validate_phone(phone):
    """Validate Indian phone number (10 digits). Returns error message or None."""
    if not phone:
        return None  # phone is optional in some forms
    digits = re.sub(r'[\s\-\+]', '', phone)
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    if not re.match(r'^\d{10}$', digits):
        return "Phone must be a valid 10-digit number"
    return None


def validate_name(name):
    """Validate name - only letters, spaces, dots, hyphens. Returns error message or None."""
    if not name:
        return "Name is required"
    if len(name) < 2:
        return "Name must be at least 2 characters"
    if not re.match(r'^[a-zA-Z\s.\-]+$', name):
        return "Name can only contain letters, spaces, dots and hyphens"
    return None


def validate_password(password):
    """Validate password strength. Returns error message or None."""
    if not password:
        return "Password is required"
    if len(password) < 6:
        return "Password must be at least 6 characters"
    if not re.search(r'[A-Za-z]', password):
        return "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return "Password must contain at least one number"
    return None


def validate_age(age):
    """Validate age. Returns error message or None."""
    if not age:
        return None
    try:
        age_int = int(age)
        if age_int < 1 or age_int > 120:
            return "Age must be between 1 and 120"
    except (ValueError, TypeError):
        return "Age must be a valid number"
    return None


def validate_fields(data, rules):
    """
    Validate multiple fields at once.
    data: dict of field_name -> value
    rules: dict of field_name -> list of validator functions
    Returns first error found or None.
    """
    for field, validators in rules.items():
        value = data.get(field)
        for validator in validators:
            error = validator(value)
            if error:
                return error
    return None
