from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    def __init__(self, url: str, content: str, downloaded_at: datetime, created_at: list[str], creators: list[str],
                 links: list[str], image_urls: list[str]):
        self.url: str = url
        self.content: str = content
        self.downloaded_at: datetime = downloaded_at
        self.created_ad: list[str] = created_at
        self.creators: list[str] = creators
        self.links: list[str] = links
        self.image_urls: list[str] = image_urls
