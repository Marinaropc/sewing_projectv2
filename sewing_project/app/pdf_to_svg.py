import os
import subprocess
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject
from pdf2image import convert_from_path
import pytesseract


def get_required_rotation(pdf_path, page_number):
    """
    Render one page very low-res, ask Tesseract which way is up.
    Returns: 0, 90, or -90 (degrees).
    """
    try:
        img = convert_from_path(pdf_path, dpi=100,
                                first_page=page_number,
                                last_page=page_number)[0]
        osd = pytesseract.image_to_osd(img)
        if "Rotate: 90" in osd:
            return 90          # needs clockwise rotation
        if "Rotate: 270" in osd:
            return -90         # needs counter-clockwise rotation
    except Exception as e:
        # print(f"OSD failed on page {page_number}: {e}")
        pass
    return 0                   # assume right-way-up


def convert_pdf_to_svgs(pdf_path, output_dir):
    """
    Convert each page of a PDF to an individual SVG using pdf2svg.
    Returns a list of SVG file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    svg_paths = []

    reader = PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        rotation = get_required_rotation(pdf_path, i + 1)
        if rotation:
            page.rotate(rotation)
            print(f"[auto-rotate] page {i + 1} rotated {rotation}°")
        single_page_pdf = os.path.join(output_dir, f"temp_page_{i + 1}.pdf")
        output_svg = os.path.join(output_dir, f"page_{i + 1}.svg")
        writer = PdfWriter()
        # Ensure /Resources is present for Inkscape
        if "/Resources" not in page:
            page[NameObject("/Resources")] = writer._add_object(DictionaryObject())
        writer.add_page(page)
        with open(single_page_pdf, "wb") as f:
            writer.write(f)
        cmd = [
            "pdf2svg",
            single_page_pdf,
            output_svg,
            "1"
        ]
        try:
            subprocess.run(cmd, check=True)
            if os.path.exists(output_svg):
                svg_paths.append(output_svg)
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert page {i+1}: {e}")
        # Only remove temp PDF after confirming SVG conversion
        if os.path.exists(single_page_pdf):
            os.remove(single_page_pdf)
    return svg_paths