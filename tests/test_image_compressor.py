from PIL import Image
from ihatepdf.core.image_compressor import (
    get_image_info,
    compress_image,
    CompressionLevel,
)


def _create_sample_jpeg(path, width=400, height=300):
    img = Image.new("RGB", (width, height), color="red")
    img.save(path, format="JPEG", quality=95)


def _create_sample_png(path, width=400, height=300):
    img = Image.new("RGBA", (width, height), color=(0, 255, 0, 255))
    img.save(path, format="PNG")


def _create_sample_webp(path, width=400, height=300):
    img = Image.new("RGB", (width, height), color="blue")
    img.save(path, format="WEBP", quality=95)


def test_get_image_info_jpeg(tmp_path):
    img_path = tmp_path / "test.jpg"
    _create_sample_jpeg(img_path, 400, 300)

    info = get_image_info(img_path)
    assert info.dimensions == (400, 300)
    assert info.file_size > 0
    assert info.format == "JPEG"


def test_compress_image_jpeg_levels(tmp_path):
    img_path = tmp_path / "photo.jpg"
    _create_sample_jpeg(img_path)

    for level in (CompressionLevel.LOW, CompressionLevel.MEDIUM, CompressionLevel.HIGH):
        out_path = tmp_path / f"photo_comp_{level.name}.jpg"
        result = compress_image(img_path, level=level, output_path=out_path)

        assert result.output_path.exists()
        assert result.original_dimensions == (400, 300)
        assert result.compressed_size > 0
        assert result.level == level

        with Image.open(out_path) as out_img:
            assert out_img.format == "JPEG"


def test_compress_image_png(tmp_path):
    img_path = tmp_path / "graphic.png"
    _create_sample_png(img_path)

    result = compress_image(img_path, level=CompressionLevel.HIGH)
    assert result.output_path.exists()
    assert result.output_path.name == "graphic_compressed.png"

    with Image.open(result.output_path) as out_img:
        assert out_img.format == "PNG"


def test_compress_image_webp(tmp_path):
    img_path = tmp_path / "modern.webp"
    _create_sample_webp(img_path)

    result = compress_image(img_path, level=CompressionLevel.MEDIUM)
    assert result.output_path.exists()
    assert result.output_path.name == "modern_compressed.webp"

    with Image.open(result.output_path) as out_img:
        assert out_img.format == "WEBP"
