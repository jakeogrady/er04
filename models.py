"""Model definitions for Anki components."""

from enum import StrEnum

from llama_index.core.bridge.pydantic import BaseModel


class AnkiCardType(StrEnum):
    """Acceptable values for Anki card types."""

    BASIC = "basic"


class AnkiCard(BaseModel):
    """Formate for Anki cards."""

    type: AnkiCardType
    front: str
    back: str


class AnkiDeck(BaseModel):
    """Format for Anki deck."""

    deck: list[AnkiCard]
