"""Module for compressing images (JPG/JPEG, PNG, WEBP) locally."""

import os
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from PIL import Image, ImageOps

from ihatepdf.utils import calculate_reduction, generate_output_path


class CompressionLevel(IntEnum):
    LOW = 1     # Low compression / High quality
    MEDIUM = 2  # Medium compression / Balanced
    HIGH = 3    # High compression / Smaller file


@dataclass(frozen=True)
class ImageInfo:
    dimensions: tuple[int, int]  # (width, height)
    file_size: int
    format: str


@dataclass(frozen=True)
class ImageCompressResult:
    input_path: Path
    output_path: Path
    original_dimensions: tuple[int, int]
    original_size: int
    compressed_size: int
    space_saved: int
    reduction_percentage: float
    level: CompressionLevel


def get_image_info(input_path: Path) -> ImageInfo:
    """Retrieve the original dimensions and file size of an image.
    
    Returns:
        ImageInfo: Dimensions (width, height), file size in bytes, and image format.
    """
    file_size = os.path.getsize(input_path)
    with Image.open(input_path) as img:
        # Apply EXIF transpose to get correct visual orientation
        transposed = ImageOps.exif_transpose(img)
        dims = (transposed.width, transposed.height) if transposed else (img.width, img.height)
        fmt = img.format or input_path.suffix.lstrip(".").upper()
        
    return ImageInfo(
        dimensions=dims,
        file_size=file_size,
        format=fmt,
    )


def compress_image(
    input_path: Path,
    level: CompressionLevel = CompressionLevel.MEDIUM,
    output_path: Path | None = None
) -> ImageCompressResult:
    """Compress an image file according to the selected compression preset.
    
    Args:
        input_path: Path to the input image file.
        level: Compression level (LOW, MEDIUM, HIGH).
        output_path: Destination path for compressed image.
        
    Returns:
        ImageCompressResult: Information about compression metrics and output location.
    """
    orig_info = get_image_info(input_path)
    orig_size = orig_info.file_size
    
    if output_path is None:
        output_path = generate_output_path(input_path, "_compressed")
        
    with Image.open(input_path) as img:
        # Normalize orientation
        working_img = ImageOps.exif_transpose(img)
        if working_img is None:
            working_img = img.copy()
            
        ext = input_path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            _compress_jpeg(working_img, output_path, level)
        elif ext == ".png":
            _compress_png(working_img, output_path, level)
        elif ext == ".webp":
            _compress_webp(working_img, output_path, level)
        else:
            # Fallback based on format
            if working_img.mode in ("RGBA", "LA", "P"):
                _compress_png(working_img, output_path, level)
            else:
                _compress_jpeg(working_img, output_path, level)

    compressed_size = os.path.getsize(output_path)
    space_saved, reduction_percentage = calculate_reduction(orig_size, compressed_size)
    
    return ImageCompressResult(
        input_path=input_path,
        output_path=output_path,
        original_dimensions=orig_info.dimensions,
        original_size=orig_size,
        compressed_size=compressed_size,
        space_saved=space_saved,
        reduction_percentage=reduction_percentage,
        level=level,
    )


def _compress_jpeg(img: Image.Image, output_path: Path, level: CompressionLevel) -> None:
    """Compress JPEG image with progressive encoding and quality presets."""
    rgb_img = img.convert("RGB") if img.mode != "RGB" else img
    
    quality_map = {
        CompressionLevel.LOW: 88,
        CompressionLevel.MEDIUM: 72,
        CompressionLevel.HIGH: 50,
    }
    quality = quality_map.get(level, 72)
    
    # In high compression mode, downsample if image is excessively large (>2560px)
    if level == CompressionLevel.HIGH:
        max_dim = 2560
        if max(rgb_img.width, rgb_img.height) > max_dim:
            rgb_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
    rgb_img.save(
        output_path,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
    )


def _compress_png(img: Image.Image, output_path: Path, level: CompressionLevel) -> None:
    """Compress PNG image using compression level and adaptive palette reduction."""
    if level == CompressionLevel.LOW:
        # Lossless standard optimization
        img.save(output_path, format="PNG", optimize=True, compress_level=6)
    elif level == CompressionLevel.MEDIUM:
        # Optimized compression
        img.save(output_path, format="PNG", optimize=True, compress_level=9)
    else:  # High compression
        # Adaptive quantization to 256-color palette if suitable, preserving alpha
        try:
            if img.mode in ("RGBA", "RGB", "LA", "L"):
                quantized = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
                quantized.save(output_path, format="PNG", optimize=True, compress_level=9)
            else:
                img.save(output_path, format="PNG", optimize=True, compress_level=9)
        except Exception:
            img.save(output_path, format="PNG", optimize=True, compress_level=9)


def _compress_webp(img: Image.Image, output_path: Path, level: CompressionLevel) -> None:
    """Compress WEBP image with quality presets."""
    quality_map = {
        CompressionLevel.LOW: 85,
        CompressionLevel.MEDIUM: 70,
        CompressionLevel.HIGH: 45,
    }
    quality = quality_map.get(level, 70)
    
    img.save(
        output_path,
        format="WEBP",
        quality=quality,
        method=6,  # Slower compression for better reduction
    )
