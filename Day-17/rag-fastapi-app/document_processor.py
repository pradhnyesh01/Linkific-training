"""
Document Processor – extracts text from PDF, TXT, DOCX and splits into chunks.
"""

import PyPDF2

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def extract_text(file_path: str, extension: str) -> str:
    """Read raw text from a file based on its extension."""
    extension = extension.lower()

    if extension == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif extension == ".pdf":
        text = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)

    elif extension == ".docx":
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    else:
        raise ValueError(f"Unsupported file type: {extension}. Supported: {SUPPORTED_EXTENSIONS}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks of roughly chunk_size characters."""
    if not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a sentence or word boundary
        if end < len(text):
            # Look for last full stop or newline within the chunk
            break_at = max(
                text.rfind(".", start, end),
                text.rfind("\n", start, end)
            )
            if break_at > start + chunk_size // 2:
                end = break_at + 1  # include the period/newline

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap  # overlap for context continuity

    return chunks
