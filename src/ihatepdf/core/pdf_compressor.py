"""Module for compressing PDF files locally and offline."""

import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter

from ihatepdf.utils import calculate_reduction, generate_output_path


@dataclass(frozen=True)
class PDFCompressResult:
    input_path: Path
    output_path: Path
    num_pages: int
    original_size: int
    compressed_size: int
    space_saved: int
    reduction_percentage: float


def get_pdf_info(input_path: Path) -> tuple[int, int]:
    """Retrieve the original file size (in bytes) and number of pages.
    
    Returns:
        tuple[int, int]: (original_size_bytes, num_pages)
    """
    orig_size = os.path.getsize(input_path)
    reader = PdfReader(str(input_path))
    num_pages = len(reader.pages)
    return orig_size, num_pages


def compress_pdf(
    input_path: Path,
    output_path: Path | None = None
) -> PDFCompressResult:
    """Compress a PDF file by compressing content streams and optimizing objects.
    
    Args:
        input_path: Path to the target PDF.
        output_path: Destination path for the compressed PDF. If None, appends '_compressed.pdf'.
        
    Returns:
        PDFCompressResult: Details of the compression results.
    """
    orig_size, num_pages = get_pdf_info(input_path)
    
    if output_path is None:
        output_path = generate_output_path(input_path, "_compressed")
        
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    
    # Clone pages into writer
    for page in reader.pages:
        writer.add_page(page)
        
    # Compress content streams
    for page in writer.pages:
        page.compress_content_streams()
        
        # Optimize embedded images if any
        try:
            for img_file in page.images:
                try:
                    raw_img = Image.open(BytesIO(img_file.data))
                    if raw_img.mode in ("RGBA", "P"):
                        # Convert to RGB with white background if saving as JPEG
                        background = Image.new("RGB", raw_img.size, (255, 255, 255))
                        if raw_img.mode == "RGBA":
                            background.paste(raw_img, mask=raw_img.split()[3])
                        else:
                            background.paste(raw_img.convert("RGBA"))
                        optimized_img = background
                    else:
                        optimized_img = raw_img.convert("RGB")
                    
                    buf = BytesIO()
                    optimized_img.save(buf, format="JPEG", quality=75, optimize=True)
                    buf.seek(0)
                    
                    # Replace image if new buffer is smaller
                    if buf.getbuffer().nbytes < len(img_file.data):
                        page.replace_image(img_file.name, buf)
                except Exception:
                    # If image replacement is not supported or fails, keep original
                    pass
        except Exception:
            pass

    # Deduplicate shared streams and dictionary objects
    try:
        try:
            writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
        except TypeError:
            writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    except Exception:
        pass
        
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
        
    compressed_size = os.path.getsize(output_path)
    space_saved, reduction_percentage = calculate_reduction(orig_size, compressed_size)
    
    return PDFCompressResult(
        input_path=input_path,
        output_path=output_path,
        num_pages=num_pages,
        original_size=orig_size,
        compressed_size=compressed_size,
        space_saved=space_saved,
        reduction_percentage=reduction_percentage,
    )
