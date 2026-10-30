---
name: suggest-anki-cards
description: Suggest Anki card categories for German words, sentences or given cards to check, and print the chosen cards as rows to paste into a spreadsheet (Proton Sheets, Google Sheets, Excel, etc.).
argument-hint: <German words, sentences or cards to check>
allowed-tools:
  - Bash(.venv/bin/python -m scripts.suggest_anki_cards_cli *)
  - Bash(uv run --env-file .env python -m scripts.suggest_anki_cards_cli lookup *)
---

# Suggest Anki Cards

Input: $ARGUMENTS

Category abbreviations the input may use:
- `EAP` = `DEU → ENG ⋀ ARTIKEL ⋀ PLURAL`
- `E` = `DEU → ENG`
- `AP` = `ARTIKEL ⋀ PLURAL`
- `DGV` = `DAS GEGENTEIL VON`
- `QF` = `QUIZFRAGE`

`list` output with the categories and their formats and example cards, the translation separator, the no-plural value and the allowed suffix tags by the language of the term each follows:

!`.venv/bin/python -m scripts.suggest_anki_cards_cli list`

1. Work from the `list` output above for categories, formats, separators and suffix tags; never work from memory.
2. For each input entry, use the categories the input names; otherwise ask with one multi-select `AskUserQuestion` question per entry, quoting that entry's whole input line verbatim in the question and keeping its header from reading as part of another entry, offering up to 4 categories whose example shows the entry fits, with `QUIZFRAGE` only as a last resort per `QUIZFRAGE Card Selection and Wording`.
3. Draft one card per selected category, shaped like its example, in plain text without HTML tags such as `<br>` unless the example has them, and writing German nouns with their definite article unless the card tests it, and separable verb infinitives with `*`, e.g. `ab*holen`. Draft a `QUIZFRAGE` card following `QUIZFRAGE Card Selection and Wording`. Draft each English translation as its own card, e.g. `a` → `b` and `a` → `c`, and apply these rules to each:
   - Synthesize the best translation from all translation sources, trusting them in this order without discarding a lower source just because a higher one has an answer:
     1. Translator: run `uv run --env-file .env python -m scripts.suggest_anki_cards_cli lookup <German words>` once with every entry's German words and weigh its candidates by confidence and back-translations; stop and show the error if it fails.
     2. Online searches, all issued in parallel in one turn.
     3. Your own validated memory.
     4. The user's notes and any card text in the input, always only suggestions.
   - Use the shortest common equivalent that translates back to this German word, not to a near-synonym, in US spelling, e.g. `to organize`, not `to organise`. If the meaning depends on context, add one card per common sense, as few as cover them.
   - Start verbs with `to`, and mark `[adj]` or `[adv]` on both the German word and the translation, e.g. `witzig [adj]` → `witty [adj]`. Mark `[pl]` on a term that is grammatically plural and `[sg]` on a term that looks plural but is singular, judging the German word and the translation each on its own, e.g. `die Möbel [pl]` → `furniture` and `die Nachricht` → `news [sg]`. For a person noun that has both a male and a female form, mark `[m.]` or `[f.]` on the translation, and also on the German word when its form is the same for both genders, e.g. `Prominente [f.]` → `celebrity [f.]` but `Richterin` → `judge [f.]`. The translation's `sth.`/`sb.` must match the German word's `etw.`/`jmdn.`/`jmdm.`/`jmds.`, e.g. `etw. ab*geben` → `to submit sth.`; leave out senses that don't.
   - Put a German suffix tag at the end of the German term and an English suffix tag at the end of the English term, as `list` assigns them, e.g. `gekommen [part.II]` → `come [pp]`.
   - If a translation, whichever source it came from, could still be read as another German word or sense than the card means, add the fewest of the suffix tags `list` prints (such as `[noun]`, never a made-up `[…]` tag) and/or `(e.g. …)` usage examples until it can't, without repeating the translation.
4. Verify that every card is factually correct, fixing and rechecking until a full pass finds nothing off. Then merge each entry's translation cards of one category with the translation separator into `a` → `b | c`, and trim the merged card to at most two translations, keeping a third or more only when each names a sense of the German word distinct from every other kept translation. Trim carefully, keeping the translations that the most and highest-ranked translation sources of step 3 confirm. On the trimmed card, keep an `[adj]` or `[adv]` tag on the German term only when every remaining translation carries it; otherwise drop that tag from the German term and every translation, and tell the senses apart with `(e.g. …)` usage examples instead. Leave the format checks that `build --help` lists to `build` in step 6 rather than rechecking them here.
5. For each entry with a translation, print its `lookup` output unchanged, then one short sentence per translation justifying it, followed by 1–2 translated example sentences under `**Examples:**` in a `| **DEU** | **ENG** |` table with the entry and its translation in `***…***`.
6. Pass the merged cards as one JSON argument to `.venv/bin/python -m scripts.suggest_anki_cards_cli build` (see `--help` for the input), fix any card it rejects, and print its output unchanged in one code block. Do not edit repository files.
7. Revise from the relevant step on the user's feedback until they approve the output; only then copy the approved `build` output to the clipboard, keeping the tabs and without a trailing newline.

## QUIZFRAGE Card Selection and Wording

- Suggest `QUIZFRAGE` only for a semi-structured or unstructured fact that no other category can test, since its free-form cards lack the fixed format that keeps the other categories consistent.
- Make a `QUIZFRAGE` card test the fact the input names, and ask the user for that fact when the input leaves it unclear, instead of guessing one or falling back to a translation or a grammar term the input doesn't mention.
- Treat these `QUIZFRAGE` wording rules as defaults, not a checklist: judge each card by how well it teaches, and break a rule when following it makes the card worse, saying which rule and why.
- Test one fact per `QUIZFRAGE` card, splitting a combined question into several cards.
- Word a `QUIZFRAGE` front so it has exactly one definite answer, never as an open-ended comparison or explanation.
- Write a `QUIZFRAGE` card in German, joining the options on its front with ` ODER ` only when picking among them takes real knowledge; ask for free recall instead when the choice is a near 50/50 guess or the front already gives the answer away.
- Word every `QUIZFRAGE` front as a short question understood at a glance, even when another rule pulls the other way: lead with what is asked, put any context after it, and quote only the example word, phrase or sentence the question asks about in „…“, never the question's own words, e.g. `Akkusativergänzung in „Sie informierte den Kunden“?` rather than `„Sie informierte den Kunden“ — Akkusativergänzung = ?`.
- Ask about a sentence on a `QUIZFRAGE` front by quoting it whole with a gap or with the word to place, not by listing loose words to assemble under extra conditions.
- Keep `:` off a `QUIZFRAGE` front, since `AnkiCard` rejects any `:` after the category prefix, and keep off it any symbol that adds no meaning or already means something else in the deck.
- Give a `QUIZFRAGE` front only enough context to rule out other correct answers, without hinting at the answer.
- Put the bare answer on a `QUIZFRAGE` back, adding one short example in parentheses only when it shows something the answer alone doesn't.
- Keep hedges such as `meistens` off a `QUIZFRAGE` back; narrow the question or move the exception to its own card until the answer always holds.
- Split a `QUIZFRAGE` answer that is a list into one card per item.
- Cover an important rule with `QUIZFRAGE` cards from both directions, rule → example and example → rule, when each direction practises something the other doesn't.

## Category Names

- Create or rename a category in `CardCategory` and `CATEGORY_TO_FORMAT` in `scripts/shared.py`, never only in a drafted card.
- Write a category name as upper-case German grammar terms with umlauts kept, naming the front's item before what the back tests, e.g. `PRÄPOSITION REKTION`.
- Pick the precise grammar term over a word with an everyday meaning, e.g. `ADVERBIALE ANGABE` over `ANGABE`.
- Join two tested properties in a category name with ` ⋀ `, e.g. `ARTIKEL ⋀ PLURAL`, and put its scope or answer options in parentheses, e.g. `KONJUGATION (ICH/DU/ES)`.
- Keep `:` out of category names, since `AnkiCard` splits a card's front on `: `.
- Name a `CardCategory` member after the value in ASCII upper snake case with umlauts spelled `AE`/`OE`/`UE`, e.g. `PRAEPOSITION_REKTION`, and keep members alphabetical.
