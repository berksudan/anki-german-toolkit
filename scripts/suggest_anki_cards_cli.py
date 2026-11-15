import argparse
import enum
import typing

import pydantic

from scripts.card_draft import DRAFT_CARD_CHECKS_DESCRIPTION, DraftCard
from scripts.shared import (
    CATEGORY_TO_FORMAT,
    NO_PLURAL,
    TRANSLATION_SEPARATOR,
    AnkiCard,
    SuffixTag,
    SuffixTagLanguage,
)
from scripts.translation_suggestions import print_translation_suggestions


class _Command(enum.Enum):
    LIST = "list"
    BUILD = "build"
    LOOKUP = "lookup"
    PREVIEW = "preview"


def _print_suggestible_categories() -> None:
    print(f"Translation separator: {TRANSLATION_SEPARATOR!r}")
    print(f"{{OPTIONAL_PLURAL}} for a noun without a plural: {NO_PLURAL!r}")
    for language in SuffixTagLanguage:
        tags = ", ".join(
            tag.value.text for tag in SuffixTag if tag.value.language is language
        )
        print(f"Suffix tags after the {language.value} term: {tags}")
    for category, card_format in CATEGORY_TO_FORMAT.items():
        print(f"{category}\t{card_format.template}\te.g. {card_format.example}")


def _validate_cards(*, drafts_json: str) -> list[AnkiCard]:
    drafts = pydantic.TypeAdapter(list[DraftCard]).validate_json(drafts_json)
    return [
        AnkiCard(front=f"{draft.category}: {draft.front}", back=draft.back)
        for draft in drafts
    ]


def _escape_markdown_cell(text: str) -> str:
    return text.replace("|", r"\|")


def _print_validated_rows(*, drafts_json: str) -> None:
    for card in _validate_cards(drafts_json=drafts_json):
        print(f"{card.category}\t{card.front_without_category}\t{card.back}")


def _print_validated_table(*, drafts_json: str) -> None:
    print("| Category | Front | Back |")
    print("| --- | --- | --- |")
    for card in _validate_cards(drafts_json=drafts_json):
        print(
            f"| {card.category}"
            f" | {_escape_markdown_cell(card.front_without_category)}"
            f" | {_escape_markdown_cell(card.back)} |"
        )


def _dispatch_command_from_cli() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "`list`: print the translation separator, the no-plural value, "
            "the allowed `[…]` suffix tags by the language of the term they "
            "follow and the suggestible "
            "categories with their `front;back` format and an example card. "
            '`build JSON`: take a JSON list of {"category", "front", "back"}, '
            "shaped like each category's example, validate each card against "
            f"{DRAFT_CARD_CHECKS_DESCRIPTION}, and print it "
            "as a tab-separated spreadsheet row. "
            "`preview JSON`: validate the same input as `build` and print the "
            "cards as a Markdown table with Category, Front and Back columns. "
            "`lookup WORD...`: print a Markdown table of Azure dictionary "
            "translations per German word with part of speech, confidence, "
            "back-translations with their frequency counts and, when another "
            "German word is the most frequent back-translation, that word "
            "(needs the variables from `.env`)."
        )
    )
    parser.add_argument("command", choices=[command.value for command in _Command])
    parser.add_argument("inputs", nargs="*")
    arguments = parser.parse_args()
    match _Command(arguments.command):
        case _Command.LIST:
            _print_suggestible_categories()
        case _Command.BUILD:
            (drafts_json,) = arguments.inputs
            _print_validated_rows(drafts_json=drafts_json)
        case _Command.LOOKUP:
            print_translation_suggestions(german_words=arguments.inputs)
        case _Command.PREVIEW:
            (drafts_json,) = arguments.inputs
            _print_validated_table(drafts_json=drafts_json)
        case unreachable:
            typing.assert_never(unreachable)


if __name__ == "__main__":
    _dispatch_command_from_cli()
