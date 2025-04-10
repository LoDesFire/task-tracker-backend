import random


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
    special = "!@#$%*_+-={}?"

    digit_count = max(0, int(length * digit_percent / 100))
    special_count = max(0, int(length * special_percent / 100))
    letter_count = length - digit_count - special_count

    password_digits = random.choices(digits, k=digit_count)
    password_special = random.choices(special, k=special_count)
    password_letters = random.choices(lowercase + uppercase, k=letter_count)

    password = password_digits + password_special + password_letters
    random.shuffle(password)

    return "".join(password)


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


if __name__ == "__main__":
    print(generate_verification_code())
