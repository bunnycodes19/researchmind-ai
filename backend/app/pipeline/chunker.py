from dataclasses import dataclass

from app.pipeline.cleaner import clean_page_text, detect_section
from app.pipeline.pdf_extractor import PageText


@dataclass
class TextChunk:
    content: str
    page_number: int
    section_name: str
    char_start: int
    char_end: int
    chunk_index: int


def chunk_pages(
    pages: list[PageText],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    section = "Introduction"
    global_offset = 0
    buffer = ""
    buffer_page = 1
    buffer_section = section
    chunk_index = 0

    def flush_buffer(buf: str, page: int, sec: str, start: int) -> None:
        nonlocal chunk_index
        if not buf.strip():
            return
        pos = 0
        while pos < len(buf):
            end = min(pos + chunk_size, len(buf))
            piece = buf[pos:end].strip()
            if piece:
                chunks.append(
                    TextChunk(
                        content=piece,
                        page_number=page,
                        section_name=sec,
                        char_start=start + pos,
                        char_end=start + end,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
            if end >= len(buf):
                break
            pos = end - overlap

    for page in pages:
        cleaned = clean_page_text(page.text)
        for line in cleaned.split("\n"):
            section = detect_section(line, section)
        segment = f"\n\n[Page {page.page_number}]\n{cleaned}"
        if len(buffer) + len(segment) > chunk_size * 2:
            flush_buffer(buffer, buffer_page, buffer_section, global_offset)
            tail = buffer[-overlap:] if overlap < len(buffer) else ""
            buffer = tail + segment
            global_offset += len(buffer) - len(segment)
        else:
            if not buffer:
                buffer_page = page.page_number
                buffer_section = section
            buffer += segment
        section = detect_section(cleaned.split("\n")[0] if cleaned else "", section)

    flush_buffer(buffer, buffer_page, buffer_section, global_offset)
    return chunks
