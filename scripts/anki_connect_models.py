import enum

import pydantic
from pydantic.alias_generators import to_camel

_CAMEL_CASE_CONFIG = pydantic.ConfigDict(
    frozen=True,
    alias_generator=to_camel,
    validate_by_name=True,
    serialize_by_alias=True,
)


class OperationState(enum.Enum):
    CANCELLED = "cancelled"
    FAILED = "failed"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    WAITING_FOR_USER = "waitingForUser"


class AnkiConnectReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    error: str | None


class FrontBackFieldNamesReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    result: tuple[str, str]


class NoteIdsReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    result: tuple[int, ...]


class NoteFieldContent(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    value: str


class NoteInfo(pydantic.BaseModel):
    model_config = _CAMEL_CASE_CONFIG
    note_id: int
    fields: dict[str, NoteFieldContent]


class NotesInfoReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    result: tuple[NoteInfo, ...]


class RpcError(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    message: str


class RpcReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    error: RpcError | None = None


class OperationReference(pydantic.BaseModel):
    model_config = _CAMEL_CASE_CONFIG
    operation_id: str


class OperationStartReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    result: OperationReference


class OperationStatus(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    state: OperationState
    error: RpcError | None = None


class OperationStatusReply(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    result: OperationStatus


class NoParams(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)


class ModelFieldNamesParams(pydantic.BaseModel):
    model_config = _CAMEL_CASE_CONFIG
    model_name: str


class FindNotesParams(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    query: str


class NoteIdsParams(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    notes: tuple[int, ...]


class NewNote(pydantic.BaseModel):
    model_config = _CAMEL_CASE_CONFIG
    deck_name: str
    model_name: str
    fields: dict[str, str]


class AddNoteParams(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    note: NewNote


class NoteFieldsUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    id: int
    fields: dict[str, str]


class UpdateNoteFieldsParams(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)
    note: NoteFieldsUpdate
