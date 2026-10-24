# Secrets and the boundary of what Claude may see

What Claude can read, can end up in its context, in a log, in a commit message or in a wiki page. So there are two questions: what is in git, and what Claude can reach.

## Five layers, each catches what the previous one misses

| Layer | What it does | Where |
|---|---|---|
| 1. Keep secrets out of the repo | Keys, certificates and passwords live outside the working tree, in a secret manager or a key store | Your team's vault, Windows Credential Manager, a hardware security module for production keys |
| 2. `.gitignore` | Files that must exist locally never get committed | `.gitignore` in every repo: `.env`, `*.pem`, `*.key`, `keys/`, `secrets/` |
| 3. Environment variables | Code reads `os.environ["SIGNING_KEY_PATH"]`, never a literal; build scripts get secrets from the environment or the vault at build time | Build scripts, CI |
| 4. Claude Code permissions | `deny` rules stop the Read, Edit and Write tools on secret paths | `.claude/settings.json` (shared) or `~/.claude/settings.json` (everywhere) |
| 5. A hook as safety net | Blocks any tool call, including Bash and PowerShell, that touches a protected path, and blocks writing text that looks like a key | `.claude/hooks/guard_secrets.py` |

Plus a pre-commit check as the last line: `python tools/scan_secrets.py --staged`.

## Why layer 5 matters on Windows

A deny rule such as `Read(**/.env)` stops Claude's Read tool. It does not stop `cat .env` or `Get-Content .env` in a shell. On macOS, Linux and WSL2 the Claude Code sandbox can extend file rules to shell commands; on native Windows there is no sandbox. The hook closes that gap by checking shell commands too.

## Set it up

1. Copy `.claude/settings.json` and `.claude/hooks/` into each repo (or put the rules in `~/.claude/settings.json` to cover every project).
2. Add your own key file names to `.claude/hooks/secret_paths.txt`.
3. Install the pre-commit check:

   ```bash
   printf '#!/bin/sh\npython tools/scan_secrets.py --staged\n' > .git/hooks/pre-commit
   ```

4. Test it. In Claude Code, ask it to read a dummy `.env`, to `cat` it, and to write a fake key into a page. All three should be blocked.

## What never goes in the wiki

Keys, passwords, tokens, certificates, connection strings, personal data of customers. Write where a secret lives and who manages it. The schema in `CLAUDE.md` forbids it and `tools/wiki_lint.py` fails on anything that looks like one.

## Where to draw the line for the account

- Use a paid account with "Help improve Claude" switched off (claude.ai, Settings, Privacy), or a Team, Enterprise or API account, for anything confidential.
- Keep client and partner documents in Claude only, unless your agreements say otherwise. Other AI tools, transcription services and browser extensions each need their own decision.
- Do not send feedback or ratings from sessions that contain confidential material: `/feedback` attaches session context. `DISABLE_FEEDBACK_COMMAND=1` turns it off.
- Write the rules down once, in the wiki, so everyone draws the same line.
