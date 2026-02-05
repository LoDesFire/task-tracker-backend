import inspect
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class JWTToken:
    exp: int
    iat: int
    nbf: int
    app_id: str
    jwt_id: str
    sub: UUID
    type: str
    is_admin: bool = False
    is_verified: bool = True

    @classmethod
    def from_dict(cls, env):
        return cls(
            **{
                name: parameter.annotation(env[name])
                for name, parameter in inspect.signature(cls).parameters.items()
                if env.get(name, None) is not None
            }
        )
