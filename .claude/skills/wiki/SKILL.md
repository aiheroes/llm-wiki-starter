---
name: wiki
description: Maintain the team wiki in this repo. Use to ingest a source from raw/ into wiki pages, to answer a question from the wiki with citations, or to lint the wiki. Triggers on "ingest", "add this document to the wiki", "what does the wiki say about", "ask the wiki", "lint the wiki", "/wiki".
argument-hint: ingest <raw/file> | query <question> | lint
---

# wiki

Three operations. Read `CLAUDE.md` in the repo root first; it holds the rules every operation follows.

## ingest <raw/file>

1. **Read the source.** Never modify anything in `raw/`. For a large PDF, read the table of contents first, then only the sections that matter for the team. Note the document's title, number, version, date and author.
2. **Write the source page** `wiki/sources/<slug>.md` from `wiki/_templates/source.md`: what it covers, which version, how authoritative it is, what it does not cover.
3. **Update or create pages.** For each entity and concept the source says something about:
   - an existing page: add what is new, with a citation; keep what was there;
   - no page yet: create one from the template, `status: draft`;
   - cite like this: `(source: [[src-slug]], p. 18, §5.2.4)`.
   Exact values (register addresses, pin numbers, voltages, timings): copy them with the citation, or link to the page in the source. Never round, convert or "fix" a value.
4. **Contradictions.** When the source disagrees with a page or with another source, write both versions on the page with their citations, then add a line to `wiki/log.md` and an item to `wiki/review-queue.md`. A person decides.
5. **Index.** Add new pages to `wiki/index.md` under the right heading, one line each with a short description.
6. **Log.** Append to `wiki/log.md`: date, `ingest`, the source, pages created, pages changed, contradictions found.
7. **Report and stop.** List the changed pages with one line each, the contradictions, and the questions for the review queue. Wait for review. Do not commit unless asked.

Never write secrets (keys, passwords, tokens, certificates). If the source contains one, describe where it lives and who manages it, and tell the user.

## query <question>

1. Open `wiki/index.md`. Pick the pages that matter and follow `[[links]]` from there; read at most about eight pages before answering.
2. Answer in a few sentences or a short list. Cite each page you used as `[[page]]`.
3. For exact values, open the raw source and cite file, page and section. The wiki is a map, not the territory.
4. If the wiki has no answer, say so plainly. Then offer two options: add the question to `wiki/review-queue.md`, or ingest a source that would answer it.
5. If the answer took real work, offer to file it back: a new section or page, with the same citations.

## lint

1. Run `python tools/wiki_lint.py` and read the report.
2. Then check what a script cannot:
   - claims without a citation;
   - pages that contradict each other;
   - pages with `last_verified` older than the newest source they cite;
   - names that appear on several pages but have no page of their own;
   - pages that duplicate each other.
3. Write findings to `wiki/review-queue.md`, each with the page and a one-line proposal. Fix only mechanical items (a broken link with an obvious target, a missing index line). Ask before changing content.
4. If the script reports a possible secret: stop, show the file and line to the user, and do not repeat the value in your answer.
