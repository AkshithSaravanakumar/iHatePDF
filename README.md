# iHatePDF

```text
██╗██╗  ██╗ █████╗ ████████╗███████╗
██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝
██║███████║███████║   ██║   █████╗
██║██╔══██║██╔══██║   ██║   ██╔══╝
██║██║  ██║██║  ██║   ██║   ███████╗
╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝  ᴘᴅꜰ
```

> **Because PDFs are annoying.**

**iHatePDF** is a lightweight, offline Python CLI utility for manipulating PDFs and images locally on your machine without relying on external web servers, uploads, or AI APIs.

---

## Features (v0.1.0)

1. **Compress PDF**:
   - Compresses content streams and optimizes embedded images.
   - Shows original file size, compressed size, space saved, and reduction percentage.
   - Outputs `<filename>_compressed.pdf`.

2. **Split PDF in Half**:
   - Splits documents into two approximately equal page ranges:
     - Even count (e.g. 8 pages) $\to$ `1-4` and `5-8`
     - Odd count (e.g. 9 pages) $\to$ `1-5` and `6-9`
   - Outputs `<filename>_part1.pdf` and `<filename>_part2.pdf`.

3. **Compress Image**:
   - Supports `JPG/JPEG`, `PNG`, and `WEBP`.
   - Displays original dimensions and file size.
   - Offers 3 compression levels:
     - `1`: Low compression / High quality
     - `2`: Medium compression / Balanced
     - `3`: High compression / Smaller file
   - Outputs `<filename>_compressed.<ext>`.

---

## Installation

### Prerequisites
- Python 3.11 or higher

### Install with pip
```bash
# Clone or navigate to the project directory
cd IHatePdf

# Install in editable mode
pip install -e .

# Or install with development dependencies (pytest)
pip install -e ".[dev]"
```

---

## Usage

Simply run:
```bash
ihatepdf
```

Or via Python module:
```bash
python -m ihatepdf
```

You will see the interactive menu:
```text
Choose an operation:
  1. Compress PDF
  2. Split PDF in half
  3. Compress Image
  4. Exit
```

---

## Project Structure

```
IHatePdf/
├── pyproject.toml              # Modern Python packaging configuration
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── src/
│   └── ihatepdf/
│       ├── __init__.py         # Version definition
│       ├── __main__.py         # Module entrypoint
│       ├── cli.py              # ASCII art & interactive CLI loop
│       ├── utils.py            # Size formatting & path helpers
│       └── core/
│           ├── __init__.py
│           ├── pdf_compressor.py   # PDF compression logic
│           ├── pdf_splitter.py     # PDF splitting logic
│           └── image_compressor.py # Image compression logic (JPG, PNG, WEBP)
└── tests/
    ├── __init__.py
    ├── test_utils.py
    ├── test_pdf_splitter.py
    ├── test_pdf_compressor.py
    └── test_image_compressor.py
```

---

## Running Tests

Run the test suite using `pytest`:
```bash
pytest
```

---

## License

MIT License. Local and offline processing — your files never leave your machine.
