# LLM Wiki starter

A team wiki that Claude Code reads and maintains, plus the pieces that sit next to it in practice: subagents, a Gauntlet Loop template, and guard rails that keep secrets out of git and out of Claude's context.

Made by [AI Heroes](https://aiheroes.io) for hands-on workshops with engineering teams who already use Claude Code every day. Plain Markdown and a few small Python scripts. No database, no plugin, no vendor lock-in.

> Graph engineering decides who does what. The Gauntlet Loop decides when it is good enough. The wiki decides what everyone already knows.

## Quick start (10 minutes)

```bash
git clone https://github.com/aiheroes/llm-wiki-starter.git rnd-wiki
cd rnd-wiki
python tools/wiki_lint.py          # should report an empty, healthy wiki
claude                             # open Claude Code in the wiki repo
```

Then, inside Claude Code:

```text
/wiki ingest raw/<a document you use every week>
/wiki query <a question you keep explaining to Claude>
/wiki lint
```

Review what changed (`git diff`), fix what is wrong, commit. That review step is the point: an unreviewed summary becomes context for every later question.

## How it works

Three layers:

| Layer | Folder | Who writes it |
|---|---|---|
| Sources | `raw/` | People. Datasheets, errata, design documents, decisions, post-mortems, test procedures. Never rewritten; the source of truth |
| Wiki | `wiki/` | Claude, reviewed by people. `index.md` is the entry point, `log.md` the history, pages for entities (a chip, a board, a tool) and concepts (boot sequence, release process), linked with `[[wikilinks]]` |
| Schema | `CLAUDE.md` and `.claude/skills/wiki/` | People. The editorial rules: what a page looks like, how to ingest, how to answer, what lint checks |

Three operations, all in the `wiki` skill:

| Operation | What happens |
|---|---|
| **Ingest** | Read one source, write a source page, update or create entity and concept pages, log contradictions, update the index |
| **Query** | Start at `index.md`, follow links, open the raw source only for exact values, answer with citations |
| **Lint** | Find broken links, orphan pages, stale claims, claims without a source and anything that looks like a secret |

Two rules keep it honest:

1. **The wiki is a map, not the territory.** For exact register values, timings, voltages or contract clauses, go back to the source. Pages point to the page and section.
2. **Nothing generated goes in without review.** Every ingest ends with a human reading the diff. Pages stay `status: draft` until someone marks them `reviewed`.

## What is in this repo

| Path | What |
|---|---|
| `CLAUDE.md` | The schema, short. Always loaded when Claude runs in this repo |
| `.claude/skills/wiki/` | The ingest, query and lint procedures |
| `.claude/agents/` | Example subagents: `researcher` (read only), `builder` (own worktree), `reviewer` (fresh context, no edits), `critic` (for the Gauntlet Loop) |
| `.claude/settings.json` | Deny rules for secret files and the hook that enforces them |
| `.claude/hooks/guard_secrets.py` | Blocks tool calls that touch secret files, on every operating system |
| `raw/` | Your sources. See `raw/README.md` for naming and large PDFs |
| `wiki/` | `index.md`, `log.md`, `review-queue.md` and page templates in `wiki/_templates/` |
| `tools/wiki_lint.py` | Mechanical lint: links, orphans, stale pages, missing sources, secrets |
| `tools/scan_secrets.py` | Secret scanner for the lint and for a git pre-commit hook |
| `gauntlet/` | Prompt template for a Gauntlet Loop and an answer key for work without a reference |
| `afternoon/` | Things to build on your own after the workshop, each with a clear "done when" |
| `docs/` | Pre-flight checklist, the secrets boundary, frequent questions, and the handout |

## Plug it into your existing setup

The wiki lives in its own repo. Your code repos point to it.

**In `~/.claude/CLAUDE.md` (all projects), keep it short:**

```markdown
## Team knowledge
Our R&D wiki is at C:/work/rnd-wiki. Before answering questions about our systems, components, builds,
tests or procedures, read C:/work/rnd-wiki/wiki/index.md and follow its links.
For exact values, open the source in C:/work/rnd-wiki/raw/ and cite the page.
```

**In `~/.claude/settings.json`, give read access to the wiki folder:**

```json
{
  "permissions": {
    "additionalDirectories": ["C:/work/rnd-wiki"]
  }
}
```

**What goes where:**

| | Loaded | Holds |
|---|---|---|
| `CLAUDE.md` | Always | Short rules and pointers. Every line costs tokens in every session |
| Skills | When the task matches | Procedures: how to build, how to deploy, how to release |
| The wiki | On demand, by following links | Knowledge: what is used where, why a decision was made, what broke last time |

## Requirements

Claude Code, Git, Python 3 on the `PATH`. Obsidian is optional, for browsing and editing; the graph view is nice to look at, the value is in the structure.

## Sources

The patterns come from public work by others. See `docs/handout.md` for links and dates.

## License

MIT. Use it, change it, make it yours.
