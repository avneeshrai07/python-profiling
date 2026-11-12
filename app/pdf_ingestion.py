"""PDF generation + scraping.

No LLM is involved anywhere here. To give profilers something real to chew
on, this module actually writes PDF files to disk with fpdf2 and actually
parses them back with pypdf -- real file I/O and real (if pointless) CPU
work, standing in for "documents coming from a real corpus".
"""
import random
import time
from dataclasses import dataclass
from pathlib import Path

from fpdf import FPDF
from pypdf import PdfReader

from app.config import PDF_DIR, DEFAULT_PDF_COUNT

_WORD_BANK = (
    "retrieval augmented generation vector embedding transformer token "
    "latency throughput pipeline chunk overlap cosine similarity index "
    "query context window inference batch tensor matrix gradient model "
    "cache shard replica worker queue profiler bottleneck cpu io thread "
    "process latency buffer stream checksum hash sieve prime fibonacci"
).split()


@dataclass
class Document:
    doc_id: str
    path: Path
    text: str
    pages: int


def _random_paragraph(rng: random.Random, n_words: int = 120) -> str:
    return " ".join(rng.choice(_WORD_BANK) for _ in range(n_words))


def ensure_dummy_pdfs(n: int = DEFAULT_PDF_COUNT, force: bool = False) -> list[Path]:
    """Create n dummy multi-page PDFs under PDF_DIR if they don't already exist."""
    existing = sorted(PDF_DIR.glob("dummy_*.pdf"))
    if existing and not force:
        return existing

    for p in existing:
        p.unlink()

    rng = random.Random(1234)
    created: list[Path] = []
    for i in range(n):
        pages = rng.randint(2, 8)
        pdf = FPDF()
        for _ in range(pages):
            pdf.add_page()
            pdf.set_font("Helvetica", size=11)
            for _ in range(rng.randint(8, 18)):
                pdf.multi_cell(0, 6, _random_paragraph(rng))
                pdf.ln(1)
        out_path = PDF_DIR / f"dummy_{i:03d}.pdf"
        pdf.output(str(out_path))
        created.append(out_path)
    return created


def extract_text_from_pdf(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(texts), len(reader.pages)


def load_all_pdfs(limit: int | None = None) -> list[Document]:
    """Real disk I/O (open+read every PDF) + real CPU (text extraction)."""
    paths = sorted(PDF_DIR.glob("*.pdf"))
    if limit:
        paths = paths[:limit]

    docs: list[Document] = []
    for path in paths:
        text, pages = extract_text_from_pdf(path)
        docs.append(Document(doc_id=path.stem, path=path, text=text, pages=pages))
    return docs


def ingest_from_disk(num_dummy_pdfs: int = DEFAULT_PDF_COUNT, force_regenerate: bool = False):
    start = time.perf_counter()
    ensure_dummy_pdfs(n=num_dummy_pdfs, force=force_regenerate)
    docs = load_all_pdfs()
    elapsed = time.perf_counter() - start
    return docs, elapsed
