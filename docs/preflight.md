# Pre-flight checklist

Ten minutes, the week before the workshop. Everything here is needed in the morning; if something does not work, tell us before the day so we can fix it together.

## On your laptop

- [ ] **Claude Code is up to date.** Run `claude update`, then `claude --version`.
- [ ] **You are logged in with your own account.** Start `claude`, type `/status` and check the account.
- [ ] **"Help improve Claude" is off.** On claude.ai: Settings, Privacy. This setting also covers Claude Code on Pro and Max plans. We work with company documents on the day, so this has to be off.
- [ ] **Git works in Git Bash.** `git --version`.
- [ ] **Python 3 works in Git Bash.** `python --version` should print 3.x. The hooks and the lint script in the starter kit use it. If `python` opens the Microsoft Store, install Python from python.org and tick "Add to PATH".
- [ ] **You cloned the starter kit:** `git clone https://github.com/aiheroes/llm-wiki-starter.git rnd-wiki`, then `cd rnd-wiki` and `python tools/wiki_lint.py`. It should print an empty report.
- [ ] **You can reach your own repos and documentation** from this laptop, including network drives you use.

## Bring

- [ ] **Three documents you open every week:** a datasheet chapter, a design document, a test or release procedure. PDF, Word or Markdown.
- [ ] **The notes you already keep**, if any: Markdown files, a folder on a shared drive, your own `CLAUDE.md` and skills.
- [ ] **One question the wiki should answer** by the end of the day.
- [ ] Your charger.

## Optional

- [ ] **Obsidian** (free) to browse and edit the wiki. Not required: the wiki is plain Markdown and works in any editor.
