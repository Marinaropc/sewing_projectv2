"""
Helper functions for file handling, SVG scaling, user input extraction, and output preparation.
Used throughout the pattern upload and resizing flow.
"""
import os
from werkzeug.utils import secure_filename
from .resize import safe_float, scale_svg, resize_image, tile_image_to_a4
from zipfile import ZipFile
import re
import cairosvg


def build_user_meas_str(bust, waist, hips):
    """
    Convert bust, waist, and hips values into a formatted string for AI input.
    """
    measurements = []
    if bust:
        measurements.append(f"bust = {bust}")
    if waist:
        measurements.append(f"waist = {waist}")
    if hips:
        measurements.append(f"hips = {hips}")
    return ", ".join(measurements)


def clean_upload_dir(upload_dir):
    """
    Delete all files in the given upload directory.
    """
    for root, dirs, files in os.walk(upload_dir):
        for file in files:
            os.remove(os.path.join(root, file))


def is_file_allowed(filename, allowed_extensions):
    """
    Check if a file's extension is in the allowed list.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def prepare_upload_path(raw_filename, root_path):
    """
    Create a clean upload directory and return the secure filename, full filepath, and upload directory path.
    """
    filename = secure_filename(raw_filename)
    upload_dir = os.path.join(root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    clean_upload_dir(upload_dir)
    filepath = os.path.join(upload_dir, filename)
    return filename, filepath, upload_dir


def save_uploaded_file(file, filepath):
    """
    Save an uploaded file to disk.
    Supports SVG (text) and PDF (binary) formats.
    """
    if file.filename.lower().endswith(".svg"):
        svg_content = file.read().decode("utf-8")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return "svg"
    elif file.filename.lower().endswith(".pdf"):
        file.save(filepath)
        return "pdf"
    else:
        raise ValueError("Unsupported file type")


def get_scale_factors(original_size, bust, hips, size_chart):
    """
    Calculate scale_x and scale_y based on size chart and user measurements.
    """
    scale_x = scale_y = 1.0
    if original_size and original_size in size_chart:
        original = size_chart[original_size]
        if bust and original["bust"]:
            scale_x = bust / original["bust"]
        if hips and original["hips"]:
            scale_y = hips / original["hips"]
    return scale_x, scale_y


def extract_user_meas(request):
    """
    Extract pattern type and measurements from a Flask request.
    """
    pattern_type = request.form.get("pattern")
    bust = safe_float(request.form.get("bust"))
    waist = safe_float(request.form.get("waist"))
    hips = safe_float(request.form.get("hips"))
    original_size = request.form.get("original_size")
    return pattern_type, bust, waist, hips, original_size


def get_summary_svg_paths(filepath, upload_dir, convert_pdf_to_svgs, summarize_svg_pattern):
    """
    Convert a PDF to SVGs if needed, return a summary and the SVG paths.
    """
    if filepath.lower().endswith(".pdf"):
        svg_pages_dir = os.path.join(upload_dir, "svg_pages")
        os.makedirs(svg_pages_dir, exist_ok=True)
        svg_paths = convert_pdf_to_svgs(filepath, svg_pages_dir)
        summary = summarize_svg_pattern(svg_paths[0]) if svg_paths else "No SVG pages were created."
    else:
        svg_paths = [filepath]
        summary = summarize_svg_pattern(filepath)
    return summary, svg_paths


def prepare_resize_params(pattern_type, summary, bust, waist, hips, original_size, get_pattern_parameters):
    """
    Prepare the prompt input and call AI to get resizing parameters.
    """
    trimmed_summary = "\n".join(summary.splitlines()[:10])
    user_meas_str = build_user_meas_str(bust, waist, hips)
    resize_response = get_pattern_parameters(
        pattern_type, trimmed_summary, user_meas_str, original_size
    )
    return resize_response, user_meas_str


def generate_scaled(svg_paths, scale_x, scale_y, upload_dir):
    """
    Scale and convert SVGs to PNG, resize and tile them for printing.
    Returns lists of resized PNG and SVG file paths.
    """
    resized_svgs = []
    resized_pngs = []
    resized_dir = os.path.join(upload_dir, "resized")
    os.makedirs(resized_dir, exist_ok=True)
    for svg_path in svg_paths:
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        scaled_svg = scale_svg(svg_content, scale_x, scale_y)
        output_svg = os.path.join(resized_dir, os.path.basename(svg_path))
        with open(output_svg, "w", encoding="utf-8") as f:
            f.write(scaled_svg)
        resized_svgs.append(output_svg)
        # Convert to PNG using cairosvg
        output_png = os.path.splitext(output_svg)[0] + ".png"
        try:
            cairosvg.svg2png(url=output_svg, write_to=output_png)
            resized_png_path = output_png.replace(".png", "_resized.png")
            resize_image(output_png, resized_png_path, scale_x=3.0, scale_y=3.0)
            tiled_paths = tile_image_to_a4(resized_png_path, resized_dir)
            resized_pngs.extend(tiled_paths)
        except Exception as e:
            print(f"Error converting {output_svg} to PNG: {e}")
    return resized_pngs, resized_svgs

def scale_and_save_svg(filepath, filename, scale_x, scale_y):
    """
    Apply scaling to an SVG file and save the result.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        svg_content = f.read()
    scaled_svg = scale_svg(svg_content, scale_x, scale_y)
    output_path = os.path.join("scaled", f"scaled_{filename}")
    os.makedirs("scaled", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(scaled_svg)
    return scaled_svg, output_path


def zip_pngs(resized_pngs, upload_dir, filename):
    """
    Zip the list of resized PNG files and return the ZIP filename and path.
    """
    resized_dir = os.path.join(upload_dir, "resized")
    os.makedirs(resized_dir, exist_ok=True)
    zip_filename = f"resized_{os.path.splitext(filename)[0]}.zip"
    zip_path = os.path.join(resized_dir, zip_filename)
    with ZipFile(zip_path, 'w') as zipf:
        for png_file in resized_pngs:
            if os.path.exists(png_file):
                zipf.write(png_file, os.path.basename(png_file))
            else:
                print(f"Warning: Skipping missing file: {png_file}")
    return zip_filename, zip_path


def build_render_context(filename, bust, waist, hips, instructions, zip_filename=None, scaled_svg=None):
    """
    Prepare data dictionary to render the result HTML page.
    """
    return {
        "filename": filename,
        "bust": bust,
        "waist": waist,
        "hips": hips,
        "instructions": instructions,
        "zipfile": zip_filename,
        "scaled_svg": scaled_svg
    }


def parse_dimensions(response_text, keys):
    """
    Extract numeric values for given keys from an AI response.
    """
    values = {}
    for line in response_text.splitlines():
        line = line.replace("**", "").replace("Output:", "").strip()
        for key in keys:
            if line.lower().startswith(f"{key.lower()} ="):
                try:
                    raw_value = line.split("=", 1)[1].strip()
                    if key.lower() in ["width", "height"]:
                        values[key] = float(re.search(r"[-+]?\d*\.\d+|\d+", raw_value).group())
                    else:
                        values[key] = raw_value
                except Exception as e:
                    raise ValueError(f"Could not parse {key} from: {line} → {e}")
    if all(k in values for k in keys):
        return values
    else:
        raise ValueError(f"No valid line found with keys {keys}")