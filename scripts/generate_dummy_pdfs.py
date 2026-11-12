"""CLI wrapper to (re)generate the dummy PDF corpus used by app.pdf_ingestion.

Run from the project root as a module so the `app` package resolves:

    python -m scripts.generate_dummy_pdfs --count 20 --force
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.pdf_ingestion import ensure_dummy_pdfs  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    paths = ensure_dummy_pdfs(n=args.count, force=args.force)
    print(f"Wrote {len(paths)} dummy PDFs.")


if __name__ == "__main__":
    main()
