import json
import os
import urllib.request

import pydantic
from pydantic.alias_generators import to_camel

from scripts.shared import AnkiCard

_ANKI_CONNECT_URL = "http://127.0.0.1:8765"
_ANKI_CONNECT_VERSION = 6
_CAMEL_CASE_CONFIG = pydantic.ConfigDict(
    frozen=True,
    alias_generator=to_camel,
    validate_by_name=True,
    serialize_by_alias=True,
)


class _AnkiConnectReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    error: str | None


class _FrontBackFieldNamesReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    result: tuple[str, str]


class _ModelFieldNamesParams(pydantic.BaseModel):
    model_config = _CAMEL_CASE_CONFIG
    model_name: str


class _Note(pydantic.BaseModel):
    model_config = _CAMEL_CASE_CONFIG
    deck_name: str
    model_name: str
    fields: dict[str, str]


class _AddNoteParams(pydantic.BaseModel):
    model_config = _CAMEL_CASE_CONFIG
    note: _Note


def _post_to_anki_connect(*, action: str, params: pydantic.BaseModel) -> bytes:
    request_body = json.dumps(
        {
            "action": action,
            "version": _ANKI_CONNECT_VERSION,
            "params": params.model_dump(),
        }
    )
    request = urllib.request.Request(
        _ANKI_CONNECT_URL, data=request_body.encode(), method="POST"
    )
    with urllib.request.urlopen(request) as response:
        response_body = response.read()
    error = _AnkiConnectReply.model_validate_json(response_body).error
    if error is not None:
        raise RuntimeError("anki-connect-request-failed", error, request_body)
    return response_body


def add_anki_card(*, card: AnkiCard) -> None:
    note_type_name = os.environ["ANKI_NOTE_TYPE_NAME"]
    field_names_body = _post_to_anki_connect(
        action="modelFieldNames",
        params=_ModelFieldNamesParams(model_name=note_type_name),
    )
    front_field_name, back_field_name = _FrontBackFieldNamesReply.model_validate_json(
        field_names_body
    ).result
    note = _Note(
        deck_name=os.environ["ANKI_DECK_NAME"],
        model_name=note_type_name,
        fields={front_field_name: card.front, back_field_name: card.back},
    )
    _post_to_anki_connect(action="addNote", params=_AddNoteParams(note=note))
