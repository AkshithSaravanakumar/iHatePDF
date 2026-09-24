"""Utility functions for iHatePDF."""

from pathlib import Path


def format_size(num_bytes: int) -> str:
    """Format bytes into a human-readable string (e.g., 12.4 MB, 512.0 KB)."""
    if num_bytes < 0:
        return "0.0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    unit_index = 0
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def calculate_reduction(orig_size: int, compressed_size: int) -> tuple[int, float]:
    """Calculate space saved in bytes and reduction percentage.
    
    Returns:
        tuple[int, float]: (space_saved_bytes, reduction_percentage)
    """
    if orig_size <= 0:
        return 0, 0.0
    
    space_saved = orig_size - compressed_size
    reduction_percentage = (space_saved / orig_size) * 100.0
    return space_saved, reduction_percentage


def validate_file_path(path_str: str, allowed_extensions: tuple[str, ...]) -> Path:
    """Validate that the input path exists, is a file, and has an allowed extension.
    
    Args:
        path_str: The raw path string from the user.
        allowed_extensions: Tuple of lowercase extensions, e.g. ('.pdf',) or ('.jpg', '.png').
        
    Returns:
        Path: Resolved Path object.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is a directory or has an unsupported extension.
    """
    cleaned_path = path_str.strip().strip("'\"")
    if not cleaned_path:
        raise ValueError("File path cannot be empty.")
    
    path = Path(cleaned_path).expanduser().resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    ext = path.suffix.lower()
    allowed_lower = tuple(e.lower() for e in allowed_extensions)
    if ext not in allowed_lower:
        ext_list = ", ".join(allowed_lower)
        raise ValueError(f"Unsupported file format '{ext}'. Allowed formats: {ext_list}")
    
    return path


def generate_output_path(
    input_path: Path,
    suffix: str,
    new_extension: str | None = None
) -> Path:
    """Generate a destination path with a given suffix in the same directory.
    
    Example:
        `generate_output_path(Path("doc.pdf"), "_part1")` -> `Path("doc_part1.pdf")`
    """
    ext = new_extension if new_extension is not None else input_path.suffix
    stem = input_path.stem
    output_name = f"{stem}{suffix}{ext}"
    return input_path.parent / output_name
