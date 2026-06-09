from dataclasses import dataclass

import fitz
import pdfplumber


@dataclass
class PageText:
    page_number: int
    text: str


def extract_pdf_text(file_path: str) -> tuple[list[PageText], int, str]:
    pages: list[PageText] = []
    title = "Untitled Paper"

    doc = fitz.open(file_path)
    try:
        if doc.metadata.get("title"):
            title = doc.metadata["title"].strip() or title
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text("text")
            pages.append(PageText(page_number=i + 1, text=text))
    finally:
        doc.close()

    if sum(len(p.text.strip()) for p in pages) < 200:
        with pdfplumber.open(file_path) as pdf:
            pages = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append(PageText(page_number=i + 1, text=text))

    return pages, len(pages), title
