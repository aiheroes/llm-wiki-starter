# LLM Wiki, Gauntlet Loop and graph engineering · the short version

> Graph engineering decides who does what. The Gauntlet Loop decides when it is good enough. The wiki decides what everyone already knows.

## The wiki

- **Three layers:** `raw/` sources (never rewritten), `wiki/` pages Claude maintains (`index.md`, `log.md`, entity and concept pages, review queue), and the schema in `CLAUDE.md` plus the `wiki` skill.
- **Three operations:** ingest a source, query from the index, lint for broken links, stale pages and secrets.
- **Two rules:** the wiki is a map, not the territory, so exact values come from the source. Nothing generated goes in without review.
- **Start small:** the list of things you keep explaining to Claude is your first index.

## The Gauntlet Loop

- A lead agent gets a goal and a real bar. It splits the work into the smallest pieces that can be judged separately.
- Builders build and never grade themselves. A critic with fresh context compares candidate and reference blind, as A and B, and names the biggest remaining gap.
- Repeat until the bar is met, or until you stop it. You are the brake.
- No real reference? Write an answer key first: interview the human about every open decision.

## Graph engineering

- A loop is already a graph: nodes (agent, model call, script, human decision), edges (what happens next) and state (what is passed along).
- In Claude Code: subagents in `.claude/agents/` with their own prompt, context and tools; hooks make a transition deterministic ("tests always run before the reviewer sees it").
- Worth it when the work splits into separate pieces. Many tasks need one agent, one loop and a good stop condition.

## Secrets

- Five layers: secrets outside the repo, `.gitignore`, environment variables, deny rules in Claude Code, a hook as safety net. Plus a pre-commit scan.
- On native Windows there is no sandbox: deny rules stop the Read tool, the hook also stops `cat` and `Get-Content`.
- Never in the wiki: describe where a secret lives, never the secret.

## Sources

| What | Who, where | When |
|---|---|---|
| LLM Wiki ("an idea file") | Andrej Karpathy, gist `llm-wiki.md`: gist.github.com/karpathy/442a6bf555914893e9891c11519de94f | 4 April 2026 |
| How to Run a Gauntlet Loop | Matt Shumer, somethingbig.ai/gauntlet-loop; example repo github.com/mshumer/Claude-of-Duty | 27 July 2026 |
| Wayfinder (map of open decisions) | Matt Pocock, github.com/mattpocock/skills | 2026 |
| Answer key for the critic | Community, for example github.com/rstan251/gauntlet | August 2026 |
| Loop Engineering | Addy Osmani, addyo.substack.com/p/loop-engineering | 8 June 2026 |
| "Loop Engineering Is Dead. Enter Graph Engineering" | Hamel Husain on X; a joke about buzzword churn, the name stuck | 18 July 2026 |
| 3 years of graph engineering with LangGraph ("loops are simple graphs") | LangChain blog | 22 July 2026 |
| graph-engineering skill (nine-stage knowledge-graph pipeline plus task-graph patterns) | github.com/codejunkie99/graph-engineering | July 2026 |
| How we built our multi-agent research system (90.2% better than a single agent on an internal research eval; about 15 times the tokens of a chat) | Anthropic Engineering | 13 June 2025 |
| Context engineering, popularised | Tobi Lütke and Andrej Karpathy on X | June 2025 |
| Claude Code docs: skills, subagents, hooks, permissions, settings | code.claude.com/docs | current |
