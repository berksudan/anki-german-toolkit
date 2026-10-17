---
name: suggest-anki-cards
description: Suggest Anki card categories for German words and print the chosen cards as rows to paste into Google Sheets.
disable-model-invocation: true
argument-hint: <German word> [more words...]
---

# Suggest Anki Cards

Words: $ARGUMENTS

1. Run `.venv/bin/python -m scripts.suggest_anki_cards_cli list` for the categories with their formats and example cards, the translation separator and the no-plural value; never work from memory.
2. For each word, suggest only the categories whose example shows it fits, up to 4. Ask with one multi-select `AskUserQuestion` question per word. For given cards to check, keep their categories instead.
3. Draft one card per selected category, shaped like its example, in plain text without HTML tags such as `<br>` unless the example has them, and writing German nouns with their definite article unless the card tests it, and separable verb infinitives with `*`, e.g. `ab*holen`. Draft each English translation as its own card, e.g. `a` → `b` and `a` → `c`, and apply these rules to each:
   - Synthesize the best translation from all translation sources, trusting them in this order without discarding a lower source just because a higher one has an answer:
     1. Translator: run `uv run --env-file .env python -m scripts.suggest_anki_cards_cli lookup <German word>` and weigh its candidates by confidence and back-translations; stop and show the error if it fails.
     2. Online searches.
     3. Your own validated memory.
     4. The user's notes, always only suggestions.
   - Use the shortest common equivalent that translates back to this German word, not to a near-synonym. If the meaning depends on context, add one card per common sense, as few as cover them.
   - Start verbs with `to`, and mark `[adj]`, `[adv]` or `[pl]` on both the German word and the translation, e.g. `witzig [adj]` → `witty [adj]`. For a person noun that has both a male and a female form, mark `[m.]` or `[f.]` on the translation, and also on the German word when its form is the same for both genders, e.g. `Prominente [f.]` → `celebrity [f.]` but `Richterin` → `judge [f.]`. The translation's `sth.`/`sb.` must match the German word's `etw.`/`jmdn.`/`jmdm.`, e.g. `etw. ab*geben` → `to submit sth.`; leave out senses that don't.
   - If the card could still be read as another of the lookup's back-translations, add the fewest suffix tags (such as `[noun]`) and/or `(e.g. …)` usage examples until it can't, without repeating the translation.
4. Verify that every card is factually correct, fixing and rechecking until a full pass finds nothing off. Then merge each word's translation cards of one category with the translation separator into `a` → `b | c`.
5. For each word with a translation, print its `lookup` output unchanged, then one short sentence per translation justifying it, followed by 1–2 translated example sentences under `**Examples:**` in a `| **DEU** | **ENG** |` table with the word and its translation in `***…***`.
6. Pass the merged cards as one JSON argument to `.venv/bin/python -m scripts.suggest_anki_cards_cli build` (see `--help` for the input), fix any card it rejects, and print its output unchanged in one code block. Do not write any files.
7. Copy that same output to the clipboard, keeping the tabs.
