- Agents may commit and push directly to the default branch.
- Commit messages must not contain AI attribution such as `Co-Authored-By:` trailers, even when the agent's harness asks for one.

## AnkiConnect

- Scripts read and write the live Anki collection through the AnkiConnect add-on (code `2055492159`), installed in Anki via Tools → Add-ons → Get Add-ons, followed by an Anki restart.
- AnkiConnect only answers while the Anki desktop app is open; check it with `curl -s localhost:8765 -X POST -d '{"action":"version","version":6}'`, which returns `{"result": 6, "error": null}`.
- `scripts/anki_connect_client.py` (`AnkiConnectClient`) talks to AnkiConnect at `http://127.0.0.1:8765` (the add-on's default bind address and port) and works on the deck `ANKI_DECK_NAME` with the note type `ANKI_NOTE_TYPE_NAME`, both read from `.env` (see `.env.example`) and both required to exist in the collection.
- `AnkiConnectClient` methods: `add_card`, `find_all_cards`, `find_cards` (a non-empty Anki browser search, e.g. `PRÄPOSITION*` or `leben or haben`, wrapped in brackets so it stays limited to that deck and note type), both returning `StoredAnkiCard` with the `note_id`, `update_card` and `delete_card` (both by `note_id`), and `sync` (Anki's regular AnkiWeb sync; the other methods only change the local collection).
- AnkiConnect request and reply shapes live in `scripts/anki_connect_models.py`, and the HTTP calls with their error checks in `scripts/anki_connect_transport.py`.
- `sync` uses AnkiConnect's JSON-RPC interface at `/api/v1`, which the 2026-10-15 add-on build has and the 2025-11-09 build lacks (update via Tools → Add-ons → Check for Updates); it polls `operations.get` until the sync finishes, waits through Anki's full-sync dialog, and raises `RuntimeError` if the sync fails or is cancelled.
- Anki search reads `word:` as a field filter, so a `find_cards` query for card text containing `: ` must escape the colon, e.g. `"PRÄPOSITION ⋀ AKKUSATIV/DATIV\: leben"`.
- The note type must have exactly two fields; the card front goes into the first and the back into the second, whatever they are named (e.g. `Front`/`Back`, or `Vorderseite`/`Rückseite` in a German-language collection).
- Anki rejects a note whose first field duplicates an existing note of the same note type, and `AnkiConnectClient` raises `RuntimeError` with Anki's reason for this and any other failed request.
- Run the interactive adder with `uv run --env-file .env python -m scripts.generic_card_adder`; it first asks for a destination: `file` appends `front;back` lines to `output/new_anki_cards.csv` for a manual Anki import, `ankiconnect` adds each finished card to Anki directly and syncs with AnkiWeb once on exit, whether by Ctrl+C or by an error such as a rejected duplicate.
- Agents read cards through AnkiConnect actions such as `findNotes` (Anki browser search syntax, e.g. `deck:"Deutsche Übung"`) and `notesInfo`, not by opening `collection.anki2`, which Anki locks while running.
