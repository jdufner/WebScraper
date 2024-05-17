from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Choice:
    provided: datetime
    first: str
    second: str
    answered: datetime = field(init=False)

    def __post_init__(self):
        self.answered = datetime.now()

