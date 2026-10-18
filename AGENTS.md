- Agents may commit and push directly to the default branch.
- Commit messages must not contain AI attribution such as `Co-Authored-By:` trailers, even when the agent's harness asks for one.

## AnkiConnect

- Scripts read and write the live Anki collection through the AnkiConnect add-on (code `2055492159`), installed in Anki via Tools → Add-ons → Get Add-ons, followed by an Anki restart.
- AnkiConnect only answers while the Anki desktop app is open; check it with `curl -s localhost:8765 -X POST -d '{"action":"version","version":6}'`, which returns `{"result": 6, "error": null}`.
- `scripts/anki_connect.py` (`add_anki_card`) posts to `http://127.0.0.1:8765` (the add-on's default bind address and port) and adds a note to the deck `ANKI_DECK_NAME` with the note type `ANKI_NOTE_TYPE_NAME`, both read from `.env` (see `.env.example`) and both required to exist in the collection.
- The note type must have exactly two fields; the card front goes into the first and the back into the second, whatever they are named (e.g. `Front`/`Back`, or `Vorderseite`/`Rückseite` in a German-language collection).
- Anki rejects a note whose first field duplicates an existing note of the same note type, and `add_anki_card` raises `RuntimeError` with Anki's reason.
- Run the interactive adder with `uv run --env-file .env python -m scripts.generic_card_adder`; it first asks for a destination: `file` appends `front;back` lines to `output/new_anki_cards.csv` for a manual Anki import, `ankiconnect` adds each finished card to Anki directly.
- Agents read cards through AnkiConnect actions such as `findNotes` (Anki browser search syntax, e.g. `deck:"Deutsche Übung"`) and `notesInfo`, not by opening `collection.anki2`, which Anki locks while running.
