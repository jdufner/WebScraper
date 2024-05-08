from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    url: str
    content: str
    title: str
    downloaded_at: datetime
    created_at: list[str]
    creators: list[str]
    categories: list[str]
    links: list[str]
    image_urls: list[str]

    def created_at_or_none(self) -> datetime | None:
        if len(self.created_at) <= 0:
            return None
        return datetime.fromisoformat(self.created_at[0])

    def created_by_as_string(self) -> str | None:
        if len(self.creators) <= 0:
            return None
        return ', '.join(self.creators)
