import collections.abc
import re
import string
import typing

import pydantic

from scripts.shared import (
    CATEGORY_TO_FORMAT,
    TRANSLATION_SEPARATOR,
    BackAlternatives,
    CardCategory,
    SuffixTag,
    SuffixTagLanguage,
)

_ENGLISH_INFINITIVE_PREFIX = "to "
_ENGLISH_TRANSLATIONS_FIELD = "STR_ENGLISH"
_GERMAN_PLACEHOLDERS_BY_ENGLISH_PLACEHOLDER: dict[str, tuple[str, ...]] = {
    "sb.": ("jmdm.", "jmdn.", "jmds."),
    "sth.": ("etw.",),
}
_SEPARABLE_VERB_MARKER = "*"
DRAFT_CARD_CHECKS_DESCRIPTION = (
    "its category's `front;back` format, the `[…]` suffix tags `list` prints "
    "with the terms they follow, and, for each "
    f"`{{{_ENGLISH_TRANSLATIONS_FIELD}}}` translation, ignoring `(e.g. …)` "
    "usage examples and `(i.e. …)` glosses, matching "
    + "/".join(
        f"`{german_placeholder}`"
        for german_placeholders in _GERMAN_PLACEHOLDERS_BY_ENGLISH_PLACEHOLDER.values()
        for german_placeholder in german_placeholders
    )
    + " and "
    + "/".join(
        f"`{english_placeholder}`"
        for english_placeholder in _GERMAN_PLACEHOLDERS_BY_ENGLISH_PLACEHOLDER
    )
    + f" counts and a leading `{_ENGLISH_INFINITIVE_PREFIX}` after a separable "
    f"`{_SEPARABLE_VERB_MARKER}` verb"
)


class DraftCard(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True, extra="forbid")
    category: CardCategory
    front: str
    back: str

    @pydantic.model_validator(mode="after")
    def validate_card_rules(self) -> typing.Self:
        _validate_suffix_tags(text=self.front)
        _validate_suffix_tags(text=self.back)
        card_format = CATEGORY_TO_FORMAT[self.category]
        _, back_template = card_format.template.split(";")
        for back_alternative in _split_back_alternatives(
            back_alternatives=card_format.back_alternatives, back=self.back
        ):
            back_field_to_value = _parse_template_side(
                template_side=back_template, text=back_alternative
            )
            english_translations = back_field_to_value.get(_ENGLISH_TRANSLATIONS_FIELD)
            if english_translations is not None:
                _validate_english_translations(
                    front=self.front, english_translations=english_translations
                )
        return self


def _split_back_alternatives(
    *, back_alternatives: BackAlternatives, back: str
) -> list[str]:
    match back_alternatives:
        case BackAlternatives.NOT_ALLOWED:
            return [back]
        case BackAlternatives.JOINED_BY_TRANSLATION_SEPARATOR:
            return back.split(TRANSLATION_SEPARATOR)
        case unreachable:
            typing.assert_never(unreachable)


def _validate_english_translations(*, front: str, english_translations: str) -> None:
    german_term = _strip_usage_examples_and_glosses(text=front)
    translation_terms = [
        _strip_usage_examples_and_glosses(text=translation)
        for translation in english_translations.split(TRANSLATION_SEPARATOR)
    ]
    _validate_suffix_tag_placement(
        german_term=german_term, translations=translation_terms
    )
    _validate_object_placeholders(
        german_term=german_term, translations=translation_terms
    )
    _validate_separable_verb_translations(
        german_term=german_term, translations=translation_terms
    )


def _strip_usage_examples_and_glosses(*, text: str) -> str:
    """Remove `(e.g. …)` usage examples and `(i.e. …)` glosses, e.g. "sticky (e.g. weather) [adj]" -> "sticky [adj]"."""
    return re.sub(r" \((?:e\.g\.|i\.e\.) [^)]*\)", "", text)


def _parse_template_side(*, template_side: str, text: str) -> dict[str, str]:
    """Match text to a template side, e.g. "{A}, am {B}" + "teurer, am teuersten" -> {"A": "teurer", "B": "teuersten"}."""
    pieces = list(string.Formatter().parse(template_side))
    pattern = "".join(
        re.escape(literal) + ("" if field_name is None else f"(?P<{field_name}>.+?)")
        for literal, field_name, _spec, _conversion in pieces
    )
    template_match = re.fullmatch(pattern, text)
    if template_match is None:
        raise ValueError("text does not match template", template_side, text)
    for separator in {literal for literal, *_rest in pieces if literal.strip()}:
        if text.count(separator) != template_side.count(separator):
            raise ValueError("separator count mismatch", separator, text)
    return template_match.groupdict()


def _validate_suffix_tags(*, text: str) -> None:
    allowed_tags = {tag.value.text for tag in SuffixTag}
    # e.g. "witty [adj] [frml]" -> ["[adj]", "[frml]"]
    for tag in re.findall(r"\[[^\]]*\]", text):
        if tag not in allowed_tags:
            raise ValueError("unknown suffix tag", tag, sorted(allowed_tags))


def _validate_suffix_tag_placement(
    *, german_term: str, translations: collections.abc.Collection[str]
) -> None:
    for tag in SuffixTag:
        tag_text = tag.value.text
        match tag.value.language:
            case SuffixTagLanguage.BOTH:
                terms_with_tag = [
                    tag_text in term for term in (german_term, *translations)
                ]
                if any(terms_with_tag) and not all(terms_with_tag):
                    raise ValueError(
                        "tag must be on the German term and every translation or on none",
                        tag_text,
                        german_term,
                        translations,
                    )
            case SuffixTagLanguage.EITHER:
                pass
            case SuffixTagLanguage.ENGLISH:
                if tag_text in german_term:
                    raise ValueError(
                        "English-only tag on the German term", tag_text, german_term
                    )
            case SuffixTagLanguage.GERMAN:
                for translation in translations:
                    if tag_text in translation:
                        raise ValueError(
                            "German-only tag on a translation", tag_text, translation
                        )
            case unreachable:
                typing.assert_never(unreachable)


def _validate_object_placeholders(
    *, german_term: str, translations: collections.abc.Collection[str]
) -> None:
    for (
        english_placeholder,
        german_placeholders,
    ) in _GERMAN_PLACEHOLDERS_BY_ENGLISH_PLACEHOLDER.items():
        german_placeholder_count = sum(
            german_term.count(german_placeholder)
            for german_placeholder in german_placeholders
        )
        for translation in translations:
            if translation.count(english_placeholder) != german_placeholder_count:
                raise ValueError(
                    "placeholder count mismatch",
                    english_placeholder,
                    german_placeholders,
                    german_term,
                    translation,
                )


def _validate_separable_verb_translations(
    *, german_term: str, translations: collections.abc.Collection[str]
) -> None:
    if _SEPARABLE_VERB_MARKER in german_term:
        for translation in translations:
            if not translation.startswith(_ENGLISH_INFINITIVE_PREFIX):
                raise ValueError(
                    "separable verb translation must start with prefix",
                    _ENGLISH_INFINITIVE_PREFIX,
                    german_term,
                    translation,
                )
