"""Module containing functions which take Anki Models that process into .apkg."""

import logging
import random

import genanki
from genanki import Note

from models import AnkiCard, AnkiDeck

basic_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31),
    "Simple Model",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ],
)
logger = logging.getLogger(__name__)


def create_anki_card(card: AnkiCard) -> Note:
    """Create Anki card from the given Model."""
    if card.type.lower() == "cloze":
        note = genanki.Note(
            guid=random.randrange(1 << 30, 1 << 31),
            model=genanki.CLOZE_MODEL,
            fields=[card.front, ""],
        )
    else:
        note = genanki.Note(
            guid=random.randrange(1 << 30, 1 << 31),
            model=basic_model,
            fields=[card.front, card.back],
        )

    return note


def package_anki_deck(deck: AnkiDeck) -> None:
    """Package Anki deck from the given Model into .apkg."""
    my_deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        "Bitcoin Deck",
    )

    for card in deck.deck:
        anki_card = AnkiCard.model_validate(card)
        note = create_anki_card(anki_card)

        my_deck.add_note(note)

    package_name = f"output{random.randrange(1 << 30, 1 << 31)}.apkg"
    logger.info(f"Packaged Anki Deck {my_deck.name} - {package_name}")
    genanki.Package(my_deck).write_to_file(
        package_name,
    )
