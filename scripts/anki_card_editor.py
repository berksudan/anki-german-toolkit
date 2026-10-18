from scripts.anki_connect_client import AnkiConnectClient, StoredAnkiCard
from scripts.shared import AnkiCard


def _prompt_search_query() -> str:
    while True:
        query = input(
            "> Enter an Anki search, e.g. `leben` or `PRÄPOSITION*` (escape `:` as `\\:`): "
        ).strip()
        if query != "":
            return query
        print("> The search must not be empty! Try again..")


def _select_stored_card(*, stored_cards: list[StoredAnkiCard]) -> StoredAnkiCard:
    for index, stored_card in enumerate(stored_cards):
        print(f"\t* `{index}` for `{stored_card.card.to_str}`")
    while True:
        selection = input("> Enter a card code: ")
        if selection.isdecimal() and int(selection) < len(stored_cards):
            return stored_cards[int(selection)]
        print("> Given card code is not valid! Try again..")


def _prompt_edited_card(*, card: AnkiCard) -> AnkiCard:
    new_front_text = input(
        f"   > Enter a new front after `{card.category}: ` "
        f"(Enter keeps `{card.front_without_category}`): "
    ).strip()
    new_back = input(f"   > Enter a new back (Enter keeps `{card.back}`): ").strip()
    return AnkiCard(
        front=f"{card.category}: "
        + (card.front_without_category if new_front_text == "" else new_front_text),
        back=card.back if new_back == "" else new_back,
    )


def edit_card_in_anki(*, anki_connect_client: AnkiConnectClient) -> None:
    stored_cards = anki_connect_client.find_cards(query=_prompt_search_query())
    if len(stored_cards) == 0:
        print("[WARN] No cards found.")
        return
    stored_card = _select_stored_card(stored_cards=stored_cards)
    edited_card = _prompt_edited_card(card=stored_card.card)
    anki_connect_client.update_card(note_id=stored_card.note_id, card=edited_card)
    print(f"[INFO] Updated in Anki: `{edited_card.to_colored_str}`")
