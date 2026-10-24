# Build on your own

Pick one, finish it, then pick the next. Each card has a clear end. Work in pairs if you like; ask for help as soon as you are stuck for more than ten minutes.

## 1 · Seed the team wiki

Make the wiki real with the documents you brought.

1. Put the starter in your own git server as `rnd-wiki` (one repo for the team, everyone clones it).
2. Replace the headings in `wiki/index.md` with the things you keep explaining to Claude.
3. Ingest three documents you use every week: `/wiki ingest raw/<file>`. Review each diff before the next.
4. Ask your own question: `/wiki query <your question>`.

**Done when** your question gets an answer with citations, and `log.md` shows three ingests.

## 2 · Plug the wiki into your daily setup

1. Add the pointer from the README to `~/.claude/CLAUDE.md` and the folder to `additionalDirectories` in `~/.claude/settings.json`.
2. Move knowledge out of your global `CLAUDE.md` into wiki pages; leave pointers.
3. Open a fresh session in a code repo and ask something only the wiki knows.

**Done when** Claude reads `index.md` by itself in a fresh session, and your global `CLAUDE.md` got shorter.

## 3 · Lock the secrets

1. Copy `.claude/settings.json` and `.claude/hooks/` into a real repo; add your key file names to `secret_paths.txt`.
2. Install the pre-commit scan (see `docs/secrets.md`).
3. Create a dummy key file and try to get Claude to read it, `cat` it, and write a fake key into a page.

**Done when** all three attempts are blocked and you understand each message.

## 4 · Your first Gauntlet Loop

1. Pick a small piece of work with a reference you trust: a golden output, a test vector, a trace, a measurement.
2. Fill in `gauntlet/PROMPT.md`. No reference? Fill in `gauntlet/answer-key.md` first.
3. Run two rounds, then stop and read the log.

**Done when** the critic named a gap, a builder closed it, and the measurement shows it.

## 5 · A small team of subagents

1. Copy `.claude/agents/` into a code repo and adjust the prompts to your rules.
2. Add a hook that runs the build or the tests after edits, so the reviewer only ever sees code that builds.
3. Take one real ticket: researcher, then builder, then reviewer.

**Done when** the reviewer reports on a diff that passed the build, and you know whether this was faster than doing it in one session.

## 6 · Let Claude work with your GUI tools

1. List the steps you do by hand in the tool.
2. For each step, look for a way around the GUI: command-line options, a project or config file the tool reads, an output file, an automation interface.
3. Write one wrapper script (PowerShell, Python, `pywinauto`) for the most common step, and a skill that explains it to Claude.

**Done when** Claude runs one step of an in-house tool end to end, or you have written down why it cannot yet and what would make it possible.
