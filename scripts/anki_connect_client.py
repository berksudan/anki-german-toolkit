import dataclasses
import os
import time
import typing

from scripts.anki_connect_models import (
    AddNoteParams,
    FindNotesParams,
    FrontBackFieldNamesReply,
    ModelFieldNamesParams,
    NewNote,
    NoParams,
    NoteFieldsUpdate,
    NoteIdsParams,
    NoteIdsReply,
    NotesInfoReply,
    OperationStartReply,
    OperationState,
    OperationStatusReply,
    UpdateNoteFieldsParams,
)
from scripts.anki_connect_transport import call_anki_connect_rpc, post_to_anki_connect
from scripts.shared import AnkiCard

_SYNC_STATUS_POLL_SECONDS = 1


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class StoredAnkiCard:
    note_id: int
    card: AnkiCard


class AnkiConnectClient:
    def __init__(self) -> None:
        self._deck_name = os.environ["ANKI_DECK_NAME"]
        self._note_type_name = os.environ["ANKI_NOTE_TYPE_NAME"]
        self._scope_search = f'deck:"{self._deck_name}" note:"{self._note_type_name}"'
        field_names_body = post_to_anki_connect(
            action="modelFieldNames",
            params=ModelFieldNamesParams(model_name=self._note_type_name),
        )
        self._front_field_name, self._back_field_name = (
            FrontBackFieldNamesReply.model_validate_json(field_names_body).result
        )

    def _build_fields(self, *, card: AnkiCard) -> dict[str, str]:
        return {self._front_field_name: card.front, self._back_field_name: card.back}

    def _load_cards(self, *, search: str) -> list[StoredAnkiCard]:
        note_ids_body = post_to_anki_connect(
            action="findNotes", params=FindNotesParams(query=search)
        )
        notes_info_body = post_to_anki_connect(
            action="notesInfo",
            params=NoteIdsParams(
                notes=NoteIdsReply.model_validate_json(note_ids_body).result
            ),
        )
        return [
            StoredAnkiCard(
                note_id=note_info.note_id,
                card=AnkiCard(
                    front=note_info.fields[self._front_field_name].value,
                    back=note_info.fields[self._back_field_name].value,
                ),
            )
            for note_info in NotesInfoReply.model_validate_json(notes_info_body).result
        ]

    def add_card(self, *, card: AnkiCard) -> None:
        note = NewNote(
            deck_name=self._deck_name,
            model_name=self._note_type_name,
            fields=self._build_fields(card=card),
        )
        post_to_anki_connect(action="addNote", params=AddNoteParams(note=note))

    def find_all_cards(self) -> list[StoredAnkiCard]:
        return self._load_cards(search=self._scope_search)

    def find_cards(self, *, query: str) -> list[StoredAnkiCard]:
        return self._load_cards(search=f"{self._scope_search} ({query})")

    def update_card(self, *, note_id: int, card: AnkiCard) -> None:
        note = NoteFieldsUpdate(id=note_id, fields=self._build_fields(card=card))
        post_to_anki_connect(
            action="updateNoteFields", params=UpdateNoteFieldsParams(note=note)
        )

    def delete_card(self, *, note_id: int) -> None:
        post_to_anki_connect(
            action="deleteNotes", params=NoteIdsParams(notes=(note_id,))
        )

    def sync(self) -> None:
        sync_start_body = call_anki_connect_rpc(
            method="collection.sync", params=NoParams()
        )
        operation = OperationStartReply.model_validate_json(sync_start_body).result
        while True:
            status_body = call_anki_connect_rpc(
                method="operations.get", params=operation
            )
            status = OperationStatusReply.model_validate_json(status_body).result
            match status.state:
                case (
                    OperationState.QUEUED
                    | OperationState.RUNNING
                    | OperationState.WAITING_FOR_USER
                ):
                    time.sleep(_SYNC_STATUS_POLL_SECONDS)
                case OperationState.SUCCEEDED:
                    return
                case OperationState.FAILED | OperationState.CANCELLED:
                    raise RuntimeError(
                        "anki-connect-sync-failed", status.state, status.error
                    )
                case unreachable:
                    typing.assert_never(unreachable)
