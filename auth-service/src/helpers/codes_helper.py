import random
from collections import defaultdict

from src.settings.general_settings import settings


def generate_password(length=12, digit_percent=30, special_percent=20):
    """
    Generates a random password for the user
    :param length: password length
    :param digit_percent: percentage of digits in the password
    :param special_percent: percentage of special characters in the password
    :return: password string
    """
    digits = "23456789"  # excluded 0 and 1
    lowercase = "abcdefghijkmnpqrstuvwxyz"  # excluded o and l
    uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # excluded O and I
    special = settings.password_settings.special_characters

    digit_count = max(0, int(length * digit_percent / 100))
    special_count = max(0, int(length * special_percent / 100))
    letter_count = length - digit_count - special_count

    password_digits = random.choices(digits, k=digit_count)
    password_special = random.choices(special, k=special_count)
    password_letters = random.choices(lowercase + uppercase, k=letter_count)

    password = password_digits + password_special + password_letters
    random.shuffle(password)

    return "".join(password)


def validate_password(password: str):
    """Perform actual password validation against all rules."""
    special_chars = settings.password_settings.special_characters
    errors = []
    counts: defaultdict[str, int] = defaultdict(int)

    if len(password) < settings.password_settings.min_length:
        errors.append(
            f"Password must be at least "
            f"{settings.password_settings.min_length} characters"
        )

    for char in password:
        if char.isupper():
            counts["upper"] += 1
        elif char.islower():
            counts["lower"] += 1
        elif char.isdigit():
            counts["digit"] += 1
        elif char in special_chars:
            counts["special"] += 1
        else:
            counts["invalid"] += 1

    if counts["invalid"]:
        errors.append(
            f"Invalid characters. Only letters, digits and {special_chars} are allowed"
        )

    if settings.password_settings.is_uppercase and not counts["upper"]:
        errors.append("Password must contain at least one uppercase letter")

    if settings.password_settings.is_lowercase and not counts["lower"]:
        errors.append("Password must contain at least one lowercase letter")

    if settings.password_settings.is_digits and not counts["digit"]:
        errors.append("Password must contain at least one digit")

    if settings.password_settings.is_special_characters and not counts["special"]:
        errors.append(
            f"Password must contain at least one special character: {special_chars}"
        )

    return errors


def generate_verification_code(length=6, digit_percent=80):
    digits = "123456789"  # without 0
    uppercase = "ABCDEFGHIJKLMNPQRSTUVWXYZ"  # without O

    digit_count = max(0, int(length * digit_percent / 100))
    letter_count = length - digit_count

    code_digits = random.choices(digits, k=digit_count)
    code_letters = random.choices(uppercase, k=letter_count)
    code = code_letters + code_digits

    random.shuffle(code)

    return "".join(code)
