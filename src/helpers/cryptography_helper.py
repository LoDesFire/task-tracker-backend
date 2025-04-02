import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password with a bcrypt hash function.
    :param password: raw password to hash
    :return:
    hashed password
    """
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password hashed with a bcrypt.
    :param password: raw password
    :param hashed_password: hashed password saved in the database
    :return:
    Is password equal to hashed_password
    """
    password_bytes = password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")

    if bcrypt.hashpw(password_bytes, hashed_password_bytes) == hashed_password_bytes:
        return True

    return False
