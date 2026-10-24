# Frequent questions

Short answers to what engineering teams ask about this setup. Each one is a starting point, so test it on your own work.

**One wiki per repo, or one central wiki?**
Start with one team wiki in its own repo. Code repos point to it from their `CLAUDE.md` and get read access through `additionalDirectories`. Repo-specific facts (how this repo builds) can stay in that repo's `CLAUDE.md` or a skill; knowledge that crosses repos (which component is used where, which version goes into which product) belongs in the wiki.

**How does this relate to CLAUDE.md and skills?**
`CLAUDE.md` is short and always loaded, so keep it to rules and pointers. Skills are procedures, loaded when the task matches. The wiki is knowledge, read on demand by following links. If your global `CLAUDE.md` is long, move the knowledge parts into the wiki and leave a pointer.

**Vector database or a flat index of Markdown files?**
Start flat. An `index.md` with one line per page, and links between pages, works well up to a few hundred pages, and you can read and review every bit of it. Add search when the index no longer fits in one read: a local full-text search first, embeddings only when you have measured that people miss pages. A vector store finds similar text; the wiki stores conclusions somebody checked. They can work together.

**How big can it get, and who may write in it?**
Split pages around 150 lines, split the index by heading when it passes a few hundred lines. Everyone may propose changes; ingest goes through review like code. Decide per heading who owns it.

**Can other departments use it?**
Yes, later. Start with the team that feels the pain, learn what good pages look like, then open headings for others. Knowledge for production or after-sales often deserves its own wiki that links to the R&D one, with its own owners and its own boundary of what is in it.

**How do we keep it current?**
Make ingest part of the work: a design decision, a post-mortem or a new errata sheet gets ingested the day it lands. Run lint weekly. Close the review queue in a regular meeting.

**How do I use fewer tokens?**
Keep `CLAUDE.md` short. Let Claude read the index and two or three pages instead of whole folders. Use a cheaper model for read-only subagents (`model: sonnet` or `haiku` in the agent file). Start fresh sessions for new tasks instead of compacting forever. Use multi-agent setups only where the work splits into separate pieces: Anthropic measured multi-agent research systems at about 15 times the tokens of a chat.

**Can Claude drive our GUI tools?**
First look for a way around the GUI: a command-line mode, a config or project file the tool reads, a log it writes, or an automation interface. Claude is much better at files and commands than at clicking. If clicking is the only way, Windows UI Automation (for example `pywinauto`) or AutoHotkey scripts can be written and run by Claude. Computer use in the Claude Code CLI is macOS only for now; on Windows it is available in the Claude desktop app.

**What about a local LLM?**
Possible for search or classification on documents that may not leave the building. For the maintenance work in this setup (reading long datasheets, writing consistent pages, judging gaps) the large models are far ahead. Decide per type of document, and write that decision in the wiki.

**How do we manage API keys for scripts and CI?**
One key per purpose (CI, a test bench, a person), stored in the vault or the CI secret store, never in a repo. Set spend limits per key. Rotate on a schedule and when someone leaves. Prefer the subscription login for interactive work and keys only for automation.

**Does Obsidian matter?**
It is a pleasant editor and viewer for Markdown with links. The graph view is nice to look at; you will rarely open it. Everything here works in VS Code or any editor.
