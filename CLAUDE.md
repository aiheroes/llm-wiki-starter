# CLAUDE.md · team wiki

This repo is the team wiki. You maintain `wiki/`; people own `raw/` and this file.

## Layers

- `raw/`: sources. Read them, never edit, move or rename them.
- `wiki/`: Markdown pages you maintain. Entry point `wiki/index.md`, history `wiki/log.md`, open decisions `wiki/review-queue.md`.
- Schema: this file and `.claude/skills/wiki/SKILL.md`.

## Answering a question

Start at `wiki/index.md` and follow `[[links]]`. Answer from the wiki and cite the pages you used. For exact values (registers, pin numbers, timings, voltages, versions), open the source in `raw/` and cite file, page and section. If the wiki does not know, say so and offer to add the question to `wiki/review-queue.md`.

## Pages

- One page per entity (component, tool, repo, product) in `wiki/entities/`, per concept (start-up sequence, build process, release process) in `wiki/concepts/`, per source in `wiki/sources/`, per decision in `wiki/decisions/`. Templates in `wiki/_templates/`.
- File names in kebab-case; link with `[[file-name]]` or `[[file-name|label]]`.
- Every page has frontmatter with `type`, `sources`, `last_verified` and `status` (`draft` until a person sets `reviewed`).
- Every claim points to a source page or a raw file. No claim without a source.
- Contradictions between sources: never resolve them silently. Write both versions on the page, add an entry to `wiki/log.md` and an item to `wiki/review-queue.md`.

## Never in the wiki

Keys, passwords, tokens, certificates, connection strings, customer personal data. Describe where a secret lives and who manages it, never the secret itself. `python tools/wiki_lint.py` fails on anything that looks like one.

## Working rules

- Use the `wiki` skill for ingest, query and lint.
- Show a short summary of changed pages after every ingest and wait for review. Do not commit unless asked.
- Keep pages short. Split a page when it passes about 150 lines.
