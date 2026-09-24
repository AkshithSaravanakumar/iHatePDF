from pathlib import Path
import pytest
from ihatepdf.utils import (
    format_size,
    calculate_reduction,
    validate_file_path,
    generate_output_path,
)


def test_format_size():
    assert format_size(0) == "0 B"
    assert format_size(500) == "500 B"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1536) == "1.5 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(13002342) == "12.4 MB"
    assert format_size(1024 * 1024 * 1024) == "1.0 GB"


def test_calculate_reduction():
    saved, pct = calculate_reduction(100, 50)
    assert saved == 50
    assert pytest.approx(pct, 0.01) == 50.0

    saved, pct = calculate_reduction(1000, 250)
    assert saved == 750
    assert pytest.approx(pct, 0.01) == 75.0

    saved, pct = calculate_reduction(0, 0)
    assert saved == 0
    assert pct == 0.0


def test_validate_file_path(tmp_path):
    # Non-existent file
    with pytest.raises(FileNotFoundError):
        validate_file_path(str(tmp_path / "ghost.pdf"), (".pdf",))

    # Empty path
    with pytest.raises(ValueError, match="empty"):
        validate_file_path("", (".pdf",))

    # Existing file with wrong extension
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported file format"):
        validate_file_path(str(txt_file), (".pdf", ".jpg"))

    # Valid file
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test")
    resolved = validate_file_path(str(pdf_file), (".pdf",))
    assert resolved == pdf_file.resolve()


def test_generate_output_path():
    path = Path("/home/user/document.pdf")
    out = generate_output_path(path, "_compressed")
    assert out.name == "document_compressed.pdf"

    part = generate_output_path(path, "_part1")
    assert part.name == "document_part1.pdf"
