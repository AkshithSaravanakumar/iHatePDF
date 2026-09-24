"""Module for splitting a PDF into two approximately equal halves."""

import math
from dataclasses import dataclass
from pathlib import Path
from pypdf import PdfReader, PdfWriter

from ihatepdf.utils import generate_output_path


@dataclass(frozen=True)
class PDFSplitResult:
    total_pages: int
    part1_path: Path
    part1_range: tuple[int, int]  # (1-indexed start, 1-indexed end)
    part1_count: int
    part2_path: Path
    part2_range: tuple[int, int]  # (1-indexed start, 1-indexed end)
    part2_count: int


def calculate_split_ranges(total_pages: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Calculate the 1-indexed page ranges for splitting a document in half.
    
    For even count (e.g., 8 pages): (1, 4) and (5, 8)
    For odd count (e.g., 9 pages): (1, 5) and (6, 9)
    """
    if total_pages < 2:
        raise ValueError(f"PDF must have at least 2 pages to split. Found {total_pages} page(s).")
    
    part1_end = math.ceil(total_pages / 2)
    part2_start = part1_end + 1
    
    return (1, part1_end), (part2_start, total_pages)


def split_pdf_in_half(
    input_path: Path,
    output_dir: Path | None = None
) -> PDFSplitResult:
    """Split a PDF into two approximately equal parts.
    
    Args:
        input_path: Path to the input PDF file.
        output_dir: Optional directory to save the output files. Defaults to input directory.
        
    Returns:
        PDFSplitResult: Information about the created split files and page ranges.
    """
    reader = PdfReader(str(input_path))
    total_pages = len(reader.pages)
    
    range1, range2 = calculate_split_ranges(total_pages)
    
    part1_writer = PdfWriter()
    part2_writer = PdfWriter()
    
    # 0-indexed slicing for pypdf
    for i in range(range1[0] - 1, range1[1]):
        part1_writer.add_page(reader.pages[i])
        
    for i in range(range2[0] - 1, range2[1]):
        part2_writer.add_page(reader.pages[i])
        
    dest_dir = output_dir if output_dir is not None else input_path.parent
    part1_path = dest_dir / f"{input_path.stem}_part1.pdf"
    part2_path = dest_dir / f"{input_path.stem}_part2.pdf"
    
    with open(part1_path, "wb") as f_out:
        part1_writer.write(f_out)
        
    with open(part2_path, "wb") as f_out:
        part2_writer.write(f_out)
        
    return PDFSplitResult(
        total_pages=total_pages,
        part1_path=part1_path,
        part1_range=range1,
        part1_count=range1[1] - range1[0] + 1,
        part2_path=part2_path,
        part2_range=range2,
        part2_count=range2[1] - range2[0] + 1,
    )
