from dataclasses import dataclass, field

from flask_login import UserMixin


class User(UserMixin):
    name: str
    password: str
    is_authenticated: bool = True
    is_active: bool = True
    is_anonymous: bool = False
    id: str

    def __init__(self, name: str, password: str) -> None:
        self.name: str = name
        self.password: str = password
        self.id: str = name
