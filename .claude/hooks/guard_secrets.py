"""Claude Code PreToolUse hook: block tool calls that touch secret files or write secrets.

Wired up in .claude/settings.json. Claude Code sends the tool call as JSON on stdin. Exit code 2 blocks the call and
shows the reason to Claude; exit code 0 lets it through.

Why a hook as well as deny rules: on native Windows there is no sandbox, so a `Read(**/.env)` deny rule stops the Read
tool but not `cat .env` in Bash. This hook checks Bash and PowerShell commands too, and it checks what Claude is about
to write, so a key cannot end up in the wiki or in a commit by accident.

Protected names are in .claude/hooks/secret_paths.txt (one glob per line, `!` in front for an exception such as
`!.env.example`). Add the names your team uses for key files.
If the hook itself fails, it lets the call through and prints a warning: a broken guard should be noticed and fixed,
not lock everyone out of their session.
"""
import fnmatch
import json
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJECT, "tools"))

DEFAULT_GLOBS = [".env", ".env.*", "*.pem", "*.key", "*.pfx", "*.p12", "*.kdbx", "id_rsa*", "id_ed25519*",
                 "*credentials*", "secrets/*", "keys/*", "private/*"]


def load_globs():
    path = os.path.join(HERE, "secret_paths.txt")
    try:
        with open(path, encoding="utf-8") as f:
            globs = [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]
        return globs or DEFAULT_GLOBS
    except OSError:
        return DEFAULT_GLOBS


def norm(path):
    """Lower case, forward slashes, and Git Bash style /c/... as c:/..."""
    p = path.replace("\\", "/").lower()
    m = re.match(r"^/([a-z])/(.*)$", p)
    return f"{m.group(1)}:/{m.group(2)}" if m else p


def protected(path, globs):
    allow = [g[1:] for g in globs if g.startswith("!")]
    globs = [g for g in globs if not g.startswith("!")]
    p = norm(path)
    # Inside the project, match folder patterns on the part below the project root only. Otherwise a repo that
    # lives in, say, C:/work/private/wiki would treat every one of its own files as a secret.
    root = norm(PROJECT).rstrip("/") + "/"
    if p.startswith(root) or p == root.rstrip("/"):
        p = p[len(root):]
    parts = [x for x in p.split("/") if x]
    base = parts[-1] if parts else p
    if any(fnmatch.fnmatch(base, a.lower()) for a in allow):
        return None
    for g in globs:
        g = g.lower().strip("/")
        if "/" in g:
            folder = g.split("/", 1)[0]
            if folder in parts[:-1] or fnmatch.fnmatch(p, "*/" + g) or fnmatch.fnmatch(p, g):
                return g
        elif fnmatch.fnmatch(base, g):
            return g
    return None


def words(command):
    """Split a shell command into words, keeping quoted paths with spaces together (C:/Users/Jan de Vries/...)."""
    try:
        lex = shlex.shlex(command, posix=False, punctuation_chars=True)
        lex.whitespace_split = True
        raw = list(lex)
    except ValueError:  # unbalanced quotes: fall back to plain splitting
        raw = re.split(r"\s+", command)
    out = []
    for w in raw:
        for part in w.split("="):
            part = part.strip("'\"`()<>|;&")
            if part:
                out.append(part)
    return out


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def main():
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    globs = load_globs()

    paths = [ti.get(k) for k in ("file_path", "path", "notebook_path") if isinstance(ti.get(k), str)]
    if tool == "Glob" and isinstance(ti.get("pattern"), str):
        paths.append(ti["pattern"])
    if tool == "Grep" and isinstance(ti.get("glob"), str):
        paths.append(ti["glob"])
    for p in paths:
        hit = protected(p, globs)
        if hit:
            block(f"Blocked by guard_secrets: '{p}' matches the protected pattern '{hit}'. "
                  "Secrets stay out of Claude's context. Ask a person to handle this file.")

    if tool in ("Bash", "PowerShell") and isinstance(ti.get("command"), str):
        for w in words(ti["command"]):
            hit = protected(w, globs)
            if hit:
                block(f"Blocked by guard_secrets: the command touches '{w}' (pattern '{hit}'). "
                      "Use an environment variable or a secret manager instead of reading the file.")

    texts = [v for k, v in ti.items() if k in ("content", "new_string", "new_source") and isinstance(v, str)]
    texts += [e.get("new_string", "") for e in ti.get("edits", []) if isinstance(e, dict)]
    new_text = "\n".join(t for t in texts if t)
    if new_text:
        try:
            from scan_secrets import scan_text, is_wiki_path
        except ImportError:  # missing or outdated tools/scan_secrets.py: say so, never skip the check silently
            print("guard_secrets: tools/scan_secrets.py is missing or outdated; the text to write was NOT checked "
                  "for secrets. Copy the current tools/ folder from the starter kit.", file=sys.stderr)
            sys.exit(1)
        else:
            # Pages under wiki/ in this project get the strict check: a bare 32, 48 or 64 character hex value is a key.
            target = norm(ti.get("file_path", ""))
            root = norm(PROJECT).rstrip("/") + "/"
            rel = target[len(root):] if target.startswith(root) else target
            hits = scan_text(new_text, ti.get("file_path", "<edit>"), strict=is_wiki_path(rel))
            if hits:
                _, line, rule, masked = hits[0]
                block(f"Blocked by guard_secrets: the text to write contains a possible {rule} ({masked}, line {line}). "
                      "Never write secrets into files Claude manages. Refer to where the secret lives instead.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail open, loudly
        print(f"guard_secrets hook failed ({e}); the call was NOT checked. Fix .claude/hooks/guard_secrets.py.",
              file=sys.stderr)
        sys.exit(1)
