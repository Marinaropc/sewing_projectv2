import os
import subprocess
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject


def convert_pdf_to_svgs(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    svg_paths = []

    reader = PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        single_page_pdf = os.path.join(output_dir, f"temp_page_{i + 1}.pdf")
        output_svg = os.path.join(output_dir, f"page_{i + 1}.svg")
        writer = PdfWriter()
        # Ensure /Resources is present for Inkscape compatibility
        if "/Resources" not in page:
            page[NameObject("/Resources")] = writer._add_object(DictionaryObject())
        writer.add_page(page)
        with open(single_page_pdf, "wb") as f:
            writer.write(f)
        cmd = [
            "inkscape",
            single_page_pdf,
            "--export-filename", output_svg
        ]
        print(f"Running command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
            if os.path.exists(output_svg):
                svg_paths.append(output_svg)
        except subprocess.CalledProcessError as e:
            print(f"Failed to convert page {i+1}: {e}")
        # Only remove temp PDF after confirming SVG conversion (not in finally)
        if os.path.exists(single_page_pdf):
            os.remove(single_page_pdf)

    return svg_paths