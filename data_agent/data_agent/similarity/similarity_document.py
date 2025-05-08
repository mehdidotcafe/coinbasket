from dataclasses import dataclass
from typing import Any


@dataclass
class SimilarityDocument:
    metadata: Any | None
    page_content: Any
    id: str | None = None
