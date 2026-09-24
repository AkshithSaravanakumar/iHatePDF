import pytest
from pypdf import PdfWriter, PdfReader
from ihatepdf.core.pdf_splitter import calculate_split_ranges, split_pdf_in_half


def test_calculate_split_ranges_even():
    # 8 pages -> (1, 4) and (5, 8)
    r1, r2 = calculate_split_ranges(8)
    assert r1 == (1, 4)
    assert r2 == (5, 8)


def test_calculate_split_ranges_odd():
    # 9 pages -> (1, 5) and (6, 9)
    r1, r2 = calculate_split_ranges(9)
    assert r1 == (1, 5)
    assert r2 == (6, 9)


def test_calculate_split_ranges_min():
    # 2 pages -> (1, 1) and (2, 2)
    r1, r2 = calculate_split_ranges(2)
    assert r1 == (1, 1)
    assert r2 == (2, 2)


def test_calculate_split_ranges_too_few():
    with pytest.raises(ValueError, match="at least 2 pages"):
        calculate_split_ranges(1)


def _create_dummy_pdf(path, page_count: int):
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=200, height=200)
    with open(path, "wb") as f:
        writer.write(f)


def test_split_pdf_even_file(tmp_path):
    pdf_path = tmp_path / "sample_8pages.pdf"
    _create_dummy_pdf(pdf_path, 8)

    result = split_pdf_in_half(pdf_path)

    assert result.total_pages == 8
    assert result.part1_count == 4
    assert result.part2_count == 4
    assert result.part1_range == (1, 4)
    assert result.part2_range == (5, 8)
    assert result.part1_path.exists()
    assert result.part2_path.exists()

    reader1 = PdfReader(str(result.part1_path))
    reader2 = PdfReader(str(result.part2_path))
    assert len(reader1.pages) == 4
    assert len(reader2.pages) == 4


def test_split_pdf_odd_file(tmp_path):
    pdf_path = tmp_path / "sample_9pages.pdf"
    _create_dummy_pdf(pdf_path, 9)

    result = split_pdf_in_half(pdf_path)

    assert result.total_pages == 9
    assert result.part1_count == 5
    assert result.part2_count == 4
    assert result.part1_range == (1, 5)
    assert result.part2_range == (6, 9)

    reader1 = PdfReader(str(result.part1_path))
    reader2 = PdfReader(str(result.part2_path))
    assert len(reader1.pages) == 5
    assert len(reader2.pages) == 4
