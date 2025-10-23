from enum import StrEnum

from llama_index.core.bridge.pydantic import BaseModel


class AnkiCardType(StrEnum):
    BASIC = "basic"


class AnkiCard(BaseModel):
    type: AnkiCardType
    front: str
    back: str  # TODO do something  other than this, create logic where it is only acceptable to be empty if cloze


class AnkiDeck(BaseModel):
    deck: list[AnkiCard]
