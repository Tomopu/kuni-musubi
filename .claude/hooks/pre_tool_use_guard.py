#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path


SECRET_PATH_PATTERNS = [
    re.compile(r"(^|/)\.env($|\.local$|\.development$|\.production$|\.test$)"),
    re.compile(r"(^|/)secrets(/|$)"),
    re.compile(r"(^|/)\.ssh(/|$)"),
    re.compile(r"(^|/)\.aws(/|$)"),
    re.compile(r"(^|/)\.config/gh(/|$)"),
    re.compile(r"(^|/)\.docker/config\.json$"),
    re.compile(r"(^|/)\.npmrc$"),
    re.compile(r"(^|/)\.pypirc$"),
    re.compile(r"(^|/)\.claude/settings\.local\.json$"),
]

SECRET_COMMAND_PATTERNS = [
    re.compile(r"(^|\s)(cat|less|more|head|tail|sed|awk|grep|rg)\s+.*(^|\s)(\.env|\.ssh|\.aws|secrets)(/|\s|$)"),
    re.compile(r"(^|\s)(env|printenv|set)(\s|$)"),
    re.compile(r"(^|\s)(curl|wget|nc|netcat|scp|rsync|ssh)\s+"),
    re.compile(r"/var/run/docker\.sock"),
    re.compile(r"rm\s+-[^\n]*r[^\n]*f\s+(/|~)(\s|$)"),
]


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )
    sys.exit(0)


def as_project_relative(path_value: str, project_dir: str) -> str:
    expanded = os.path.expanduser(path_value)
    try:
        path = Path(expanded)
        if not path.is_absolute():
            path = Path(project_dir) / path
        return path.resolve().relative_to(Path(project_dir).resolve()).as_posix()
    except Exception:
        return expanded.replace("\\", "/")


def looks_secret_path(path_value: str, project_dir: str) -> bool:
    normalized = as_project_relative(path_value, project_dir)
    home_relative = os.path.expanduser(path_value).replace("\\", "/")
    return any(pattern.search(normalized) or pattern.search(home_relative) for pattern in SECRET_PATH_PATTERNS)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()

    if tool_name in {"Read", "Edit", "Write", "MultiEdit", "NotebookRead", "NotebookEdit"}:
        for key in ("file_path", "path", "notebook_path"):
            path_value = tool_input.get(key)
            if isinstance(path_value, str) and looks_secret_path(path_value, project_dir):
                deny(f"Blocked access to sensitive path: {path_value}")

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if isinstance(command, str):
            for pattern in SECRET_COMMAND_PATTERNS:
                if pattern.search(command):
                    deny("Blocked command that may expose secrets, exfiltrate data, or damage the host.")


if __name__ == "__main__":
    main()
