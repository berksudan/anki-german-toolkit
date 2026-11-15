import collections.abc

from scripts.azure_translator import (
    BackTranslation,
    DictionaryTranslation,
    fetch_dictionary_translations,
)


def _format_back_translation(*, back_translation: BackTranslation) -> str:
    return f"{back_translation.display_text} ({back_translation.frequency_count})"


def _find_other_leading_back_translation(
    *, german_word: str, translation: DictionaryTranslation
) -> BackTranslation | None:
    leading_back_translation = max(
        translation.back_translations, key=lambda back: back.frequency_count
    )
    if leading_back_translation.display_text.casefold() == german_word.casefold():
        return None
    return leading_back_translation


def print_translation_suggestions(
    *, german_words: collections.abc.Collection[str]
) -> None:
    translations_by_word = fetch_dictionary_translations(german_words=german_words)
    for word, translations in translations_by_word.items():
        print(f"**{word}**\n")
        print(
            "| Translation | Part of speech | Confidence | Back-translations"
            " | Back-translations led by another word |"
        )
        print("| --- | --- | ---: | --- | --- |")
        for translation in translations:
            back_translations = ", ".join(
                _format_back_translation(back_translation=back)
                for back in translation.back_translations
            )
            other_leading_back_translation = _find_other_leading_back_translation(
                german_word=word, translation=translation
            )
            other_leading_cell = (
                ""
                if other_leading_back_translation is None
                else _format_back_translation(
                    back_translation=other_leading_back_translation
                )
            )
            print(
                f"| {translation.display_target} | {translation.pos_tag}"
                f" | {translation.confidence:.0%} | {back_translations}"
                f" | {other_leading_cell} |"
            )
        print()
