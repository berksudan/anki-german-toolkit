---
name: suggest-anki-cards
description: Suggest Anki card categories for German words, sentences or given cards to check, and print the chosen cards as rows to paste into a spreadsheet (Proton Sheets, Google Sheets, Excel, etc.).
argument-hint: <German words, sentences or cards to check>
allowed-tools:
  - Bash(just cards-build *)
  - Bash(just cards-list)
  - Bash(just cards-lookup *)
  - Bash(just cards-preview *)
  - Bash(just duden *)
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

!`just cards-list`

1. Work from the `list` output above for categories, formats, separators and suffix tags; never work from memory.
2. For each input entry, use the categories the input names; otherwise ask with one multi-select `AskUserQuestion` question per entry, quoting that entry's whole input line verbatim in the question and keeping its header from reading as part of another entry, offering up to 4 categories whose example shows the entry fits, with `QUIZFRAGE` only as a last resort per `QUIZFRAGE Card Selection and Wording`.
3. Draft one card per selected category, shaped like its example, in plain text without HTML tags such as `<br>` unless the example has them, and writing German nouns with their definite article unless the card tests it, and separable verb infinitives with `*`, e.g. `ab*holen`. Draft a `QUIZFRAGE` card following `QUIZFRAGE Card Selection and Wording`. Draft each English translation as its own card, e.g. `a` → `b` and `a` → `c`, and apply these rules to each:
   - Synthesize the best translation from every source in `Translation Source Ranking`, trusting them in that ranking's order without discarding a lower source just because a higher one has an answer.
   - Use the shortest common equivalent that translates back to this German word, not to a near-synonym, in US spelling, e.g. `to organize`, not `to organise`. If the meaning depends on context, add one card per common sense, as few as cover them.
   - Start verbs with `to`, and mark `[adj]` or `[adv]` on both the German word and the translation, e.g. `witzig [adj]` → `witty [adj]`. Mark `[pl]` on a term that is grammatically plural and `[sg]` on a term that looks plural but is singular, judging the German word and the translation each on its own, e.g. `die Möbel [pl]` → `furniture` and `die Nachricht` → `news [sg]`. For a person noun that has both a male and a female form, mark `[m.]` or `[f.]` on the translation, and also on the German word when its form is the same for both genders, e.g. `Prominente [f.]` → `celebrity [f.]` but `Richterin` → `judge [f.]`. The translation's `sth.`/`sb.` must match the German word's `etw.`/`jmdn.`/`jmdm.`/`jmds.`, e.g. `etw. ab*geben` → `to submit sth.`; leave out senses that don't.
   - Put a German suffix tag at the end of the German term and an English suffix tag at the end of the English term, as `list` assigns them, e.g. `gekommen [part.II]` → `come [pp]`.
   - If a translation, whichever source it came from, could still be read as another German word or sense than the card means, add the fewest of the suffix tags `list` prints (such as `[noun]`, never a made-up `[…]` tag) and/or `(e.g. …)` usage examples until it can't, without repeating the translation; use an `(i.e. …)` gloss instead of examples when no short example shows the sense.
   - Word each `(e.g. …)` usage example as a typical object, subject or complement of the English translation in the card's sense, taken from that sense's common German uses, in common English words a learner knows, and continuing the translation's own construction, e.g. `to assign sb. (e.g. to a task)`, `equipment (e.g. of a car)`.
4. Verify the cards:
   - Verify that every card is factually correct, fixing and rechecking until a full pass finds nothing off.
   - Check each German word's article, plural, forms and senses against `just duden <word>`, passing the bare word without article or `*`; when it lists several matching words, rerun with `-r <n>` for each one the card could mean, e.g. `just duden Regen -r 1`.
   - Run `Translation Usage Test` on each translation, replacing one that fails with one that passes.
   - Leave the format checks that `just cards-build --help` lists to `just cards-build` rather than rechecking them here.
5. Merge each entry's translation cards of one category with the translation separator into `a` → `b | c`.
6. Trim each merged card to the fewest translations that cover the German word's common senses:
   - Keep one translation per sense, at most two in total; keep more only when each extra one names a sense no other kept translation covers.
   - Within one sense, keep the everyday word over a formal or technical one, then the translation the highest-ranked source in `Translation Source Ranking` confirms, then the one the most sources confirm.
   - Replace a translation rarely used in everyday English with an everyday word for the same sense that passes `Translation Usage Test`, keeping the rare one only when no such everyday word exists.
   - On the trimmed card, keep an `[adj]` or `[adv]` tag on the German term only when every remaining translation carries it; otherwise drop that tag from the German term and every translation, and tell the senses apart with `(e.g. …)` usage examples or `(i.e. …)` glosses instead.
7. Print one Markdown table covering every entry with a translation, one row per translation, with the bold header `| **Entry** | **Translation** | **Why** | **DEU** | **ENG** |`; in each row put the card's front in bold, the translation, one short sentence justifying it, and one example sentence with its English translation, taken from the German uses that `Translation Usage Test` ran on, with the entry and its translation in `***…***`.
8. Pass the trimmed cards as one JSON argument to `just cards-build` (see `just cards-build --help` for the input), fix any card it rejects, and print its output unchanged in one code block. Do not edit repository files.
9. Ask for approval with single-select `AskUserQuestion` questions:
   - Ask each yes/no choice left for the user, such as whether to add a card for another common use of an entry, as its own question with the options `Yes` and `No`, in the same call as the approval question and before it.
   - When the yes/no choices don't all fit beside the approval question within `AskUserQuestion`'s limit of 4 questions per call, ask all of them first in earlier calls of up to 4 questions each, revise from the relevant step on each `Yes`, and then ask the approval question alone.
   - Ask whether the user approves the cards as the last question, with the options `Approve` and `Chat about this` and, as the preview of both options, the output of `just cards-preview` run on the same JSON as `build`, unchanged.
   - Copy the `build` output to the clipboard, keeping the tabs and without a trailing newline, only when the user picks `Approve` and no other answer asks for a change.
   - When any answer asks for a change, copy nothing: after `Chat about this`, wait for the user's feedback in the chat, and take a typed `Other` answer as feedback; then revise from the relevant step and ask again.

## Translation Source Ranking

- Rank translation sources from most to least trusted in this order:
  1. Translator: run `just cards-lookup <German words>` once with every entry's German words and weigh its candidates by confidence and back-translations; stop and show the error if it fails.
  2. Online searches, all issued in parallel in one turn.
  3. Your own validated memory.
  4. The user's notes and any card text in the input, always only suggestions.

## Translation Usage Test

- Run `Translation Usage Test` on a translation by putting it in place of the German word in 2–3 of that sense's most common German uses, taken from the `Typical compounds` that `just duden` lists and from online sources, never chosen to suit the translation.
- A translation passes `Translation Usage Test` when it reads naturally in every one of those uses or, when no translation of that sense reads naturally in all of them, when no other translation of that sense reads naturally in more of them.

## QUIZFRAGE Card Selection and Wording

- Suggest `QUIZFRAGE` only for a semi-structured or unstructured fact that no other category can test, since its free-form cards lack the fixed format that keeps the other categories consistent.
- Make a `QUIZFRAGE` card test the fact the input names, and ask the user for that fact when the input leaves it unclear, instead of guessing one or falling back to a translation or a grammar term the input doesn't mention.
- Treat these `QUIZFRAGE` wording rules as defaults, not a checklist: judge each card by how well it teaches, and break a rule when following it makes the card worse, saying which rule and why.
- Test one fact per `QUIZFRAGE` card, splitting a combined question into several cards.
- Word a `QUIZFRAGE` front so it has exactly one definite answer, never as an open-ended comparison or explanation.
- Write a `QUIZFRAGE` card in German, joining the options on its front with ` ODER ` only when picking among them takes real knowledge; ask for free recall instead when the choice is a near 50/50 guess or the front already gives the answer away.
- Word every `QUIZFRAGE` front as a short question understood at a glance, even when another rule pulls the other way: lead with what is asked, put any context after it, and quote only the example word, phrase or sentence the question asks about in „…“, never the question's own words, e.g. `Akkusativergänzung in „Sie informierte den Kunden“?` rather than `„Sie informierte den Kunden“ — Akkusativergänzung = ?`.
- Ask about a sentence on a `QUIZFRAGE` front by quoting it whole with a gap or with the word to place, not by listing loose words to assemble under extra conditions.
- Write the word or part a `QUIZFRAGE` card tests in upper case on its front and back, e.g. `NICHT einfügen in „Wir sind wegen des Regens gekommen“ (Satznegation)?` → `Wir sind wegen des Regens NICHT gekommen.`, keeping context labels and any noun whose spelling the card tests in normal case.
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
