import argparse
import collections.abc
import enum
import typing

import pydantic

from scripts.azure_translator import fetch_dictionary_translations
from scripts.card_draft import DRAFT_CARD_CHECKS_DESCRIPTION, DraftCard
from scripts.shared import (
    CATEGORY_TO_FORMAT,
    NO_PLURAL,
    TRANSLATION_SEPARATOR,
    AnkiCard,
    SuffixTag,
    SuffixTagLanguage,
)


class _Command(enum.Enum):
    LIST = "list"
    BUILD = "build"
    LOOKUP = "lookup"


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


def _print_validated_rows(*, drafts_json: str) -> None:
    drafts = pydantic.TypeAdapter(list[DraftCard]).validate_json(drafts_json)
    for draft in drafts:
        card = AnkiCard(front=f"{draft.category}: {draft.front}", back=draft.back)
        print(f"{card.category}\t{card.front_without_category}\t{card.back}")


def _print_translation_suggestions(
    *, german_words: collections.abc.Collection[str]
) -> None:
    translations_by_word = fetch_dictionary_translations(german_words=german_words)
    for word, translations in translations_by_word.items():
        print(f"**{word}**\n")
        print("| Translation | Part of speech | Confidence | Back-translations |")
        print("| --- | --- | ---: | --- |")
        for translation in translations:
            back_translations = ", ".join(
                f"{back.display_text} ({back.frequency_count})"
                for back in translation.back_translations
            )
            print(
                f"| {translation.display_target} | {translation.pos_tag}"
                f" | {translation.confidence:.0%} | {back_translations} |"
            )
        print()


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
            "`lookup WORD...`: print a Markdown table of Azure dictionary "
            "translations per German word with part of speech, confidence and "
            "back-translations with their frequency counts (needs the "
            "variables from `.env`)."
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
            _print_translation_suggestions(german_words=arguments.inputs)
        case unreachable:
            typing.assert_never(unreachable)


if __name__ == "__main__":
    _dispatch_command_from_cli()
