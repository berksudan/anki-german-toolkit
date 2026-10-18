import json
import urllib.request

import pydantic

from scripts.anki_connect_models import AnkiConnectReply, RpcReply

_ANKI_CONNECT_URL = "http://127.0.0.1:8765"
_ANKI_CONNECT_RPC_URL = _ANKI_CONNECT_URL + "/api/v1"
_ANKI_CONNECT_VERSION = 6


def _post_json(*, url: str, request_body: str) -> bytes:
    request = urllib.request.Request(url, data=request_body.encode(), method="POST")
    with urllib.request.urlopen(request) as response:
        return response.read()


def post_to_anki_connect(*, action: str, params: pydantic.BaseModel) -> bytes:
    request_body = json.dumps(
        {
            "action": action,
            "version": _ANKI_CONNECT_VERSION,
            "params": params.model_dump(),
        }
    )
    response_body = _post_json(url=_ANKI_CONNECT_URL, request_body=request_body)
    error = AnkiConnectReply.model_validate_json(response_body).error
    if error is not None:
        raise RuntimeError("anki-connect-request-failed", error, request_body)
    return response_body


def call_anki_connect_rpc(*, method: str, params: pydantic.BaseModel) -> bytes:
    request_body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params.model_dump()}
    )
    response_body = _post_json(url=_ANKI_CONNECT_RPC_URL, request_body=request_body)
    error = RpcReply.model_validate_json(response_body).error
    if error is not None:
        raise RuntimeError("anki-connect-rpc-failed", error.message, request_body)
    return response_body
