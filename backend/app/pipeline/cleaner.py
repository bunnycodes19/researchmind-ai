import re

HEADER_FOOTER_RE = re.compile(
    r"^(?:\d+\s*$|page\s+\d+|copyright|©|doi:|https?://)\s*$",
    re.I | re.M,
)
NOISE_RE = re.compile(r"\s{3,}|\f+")
SECTION_RE = re.compile(
    r"^(abstract|introduction|related work|background|methodology|methods|"
    r"experiments|results|discussion|conclusion|limitations|future work|references)\s*$",
    re.I | re.M,
)


def clean_page_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if HEADER_FOOTER_RE.match(stripped):
            continue
        if len(stripped) < 3 and stripped.isdigit():
            continue
        lines.append(stripped)
    cleaned = "\n".join(lines)
    return NOISE_RE.sub("\n\n", cleaned).strip()


def detect_section(line: str, current: str) -> str:
    if SECTION_RE.match(line.strip()):
        return line.strip().title()
    return current
