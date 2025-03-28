from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    pass
