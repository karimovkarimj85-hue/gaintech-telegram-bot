from __future__ import annotations

import sys
from pathlib import Path

from docx import Document


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py extract_docx.py <path_to_docx>", file=sys.stderr)
        return 2

    docx_path = Path(sys.argv[1]).expanduser().resolve()
    d = Document(str(docx_path))

    out = "\n".join(p.text for p in d.paragraphs)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

