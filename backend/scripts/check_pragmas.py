"""Enforce the coverage pragma policy.

``# pragma: no cover`` is permitted only on defensive can't-happen branches
and typing-only blocks, and only with a same-line justification. An
unjustified pragma is how a 100% coverage gate quietly stops meaning
anything, so this fails the build rather than warning.

Run as ``python scripts/check_pragmas.py`` from the backend directory.
"""

from pathlib import Path

import re
import sys


#: A pragma, and whatever follows it on the line.
PRAGMA = re.compile(r"#\s*pragma:\s*no\s*cover(?P<justification>.*)$", re.IGNORECASE)

#: Where to look. Generated and vendored trees are not ours to police.
ROOTS = ("src", "tests", "scripts")

#: How much text after the pragma counts as an actual justification rather
#: than a shrug.
MIN_JUSTIFICATION = 15


def offences(root: Path) -> list[str]:
    """Return one message per unjustified pragma under a root.

    :param root: Directory to walk.
    :returns: Human readable messages, empty when the tree is clean.
    """
    found = []
    for path in sorted(root.rglob("*.py")):
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            match = PRAGMA.search(line)
            if match is None:
                continue
            justification = match.group("justification").strip(" -:\t")
            if len(justification) < MIN_JUSTIFICATION:
                found.append(f"{path}:{number}: pragma without a justification comment")
    return found


def main() -> int:
    """Check every root and report.

    :returns: Process exit status.
    """
    base = Path(__file__).resolve().parent.parent
    found = [
        message
        for name in ROOTS
        if (base / name).is_dir()
        for message in offences(base / name)
    ]
    if found:
        print("Coverage pragma policy violations:")
        for message in found:
            print(f"  {message}")
        print(
            "\nEvery '# pragma: no cover' needs a same-line comment saying why "
            "the branch cannot be reached."
        )
        return 1
    print("Coverage pragma policy: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
