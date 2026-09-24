from io import BytesIO
from PIL import Image
from pypdf import PdfWriter, PdfReader
from ihatepdf.core.pdf_compressor import get_pdf_info, compress_pdf


def _create_sample_pdf_with_image(path):
    writer = PdfWriter()
    page = writer.add_blank_page(width=400, height=400)
    
    # Add an uncompressed large RGB image
    img = Image.new("RGB", (300, 300), color="blue")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    with open(path, "wb") as f:
        writer.write(f)


def test_get_pdf_info(tmp_path):
    pdf_path = tmp_path / "info_test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_blank_page(width=100, height=100)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    orig_size, num_pages = get_pdf_info(pdf_path)
    assert orig_size > 0
    assert num_pages == 2


def test_compress_pdf(tmp_path):
    pdf_path = tmp_path / "compress_test.pdf"
    _create_sample_pdf_with_image(pdf_path)

    result = compress_pdf(pdf_path)

    assert result.input_path == pdf_path
    assert result.output_path.exists()
    assert result.num_pages == 1
    assert result.original_size > 0
    assert result.compressed_size > 0
    assert result.output_path.name == "compress_test_compressed.pdf"

    # Verify readable PDF output
    reader = PdfReader(str(result.output_path))
    assert len(reader.pages) == 1
