from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    def __init__(self, url: str, content: str, title: str, downloaded_at: datetime, created_at: list[str],
                 creators: list[str], links: list[str], image_urls: list[str]):
        self.url: str = url
        self.content: str = content
        self.title: str = title
        self.downloaded_at: datetime = downloaded_at
        self.created_at: list[str] = created_at
        self.creators: list[str] = creators
        self.links: list[str] = links
        self.image_urls: list[str] = image_urls

    def created_at_as_string(self) -> str:
        if len(self.created_at) <= 0:
            return ''
        return ', '.join(self.created_at)

    def created_at_or_none(self) -> datetime | None:
        if len(self.created_at) <= 0:
            return None
        return datetime.fromisoformat(self.created_at[0])

    def created_by_as_string(self) -> str | None:
        if len(self.creators) <= 0:
            return None
        return ', '.join(self.creators)
