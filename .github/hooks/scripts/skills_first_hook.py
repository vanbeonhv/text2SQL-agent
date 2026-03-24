import json
import sys


MESSAGE = (
    "Skills-first policy: before significant work, check and read applicable SKILL.md files "
    "(including superpowers/core process skills) before taking action. "
    "If unsure whether a skill applies, read it."
)


def main() -> int:
    try:
        _ = sys.stdin.read()
    except Exception:
        pass

    payload = {
        "continue": True,
        "systemMessage": MESSAGE,
    }

    json.dump(payload, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
