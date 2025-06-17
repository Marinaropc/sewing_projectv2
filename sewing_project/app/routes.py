from flask import Flask, render_template, request, send_from_directory
from .ai_calls import (get_pattern_parameters, generate_pattern_params_bikini_top,
                       generate_pattern_params_bikini_bottom, SIZE_CHART)
from .pattern_generator import generate_bikini_top, generate_bikini_bottom
import os
from .gemini_calls import get_sewing_instructions
from .pdf_to_svg import convert_pdf_to_svgs
from .svg_extract import summarize_svg_pattern
from .resize import safe_float
from .utils import (build_user_meas_str, clean_upload_dir, is_file_allowed,
                    prepare_upload_path, save_uploaded_file, get_scale_factors,
                    extract_user_meas, get_summary_svg_paths, prepare_resize_params,
                    generate_scaled, scale_and_save_svg, zip_pngs, build_render_context,
                    parse_dimensions)
from .database.db_helper import save_upload_to_db


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download_zip/<filename>")
def download_zip(filename):
    zip_dir = os.path.join(app.root_path, "uploads", "resized")
    return send_from_directory(zip_dir, filename, as_attachment=True)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """
    Handle file upload, AI-based resizing, and display the result.
    Supports both PDF and SVG formats.
    """
    if request.method == "POST":
        # Get pattern type and measurements from user
        pattern_type, bust, waist, hips, original_size = extract_user_meas(request)

        file = request.files.get("svg_file")
        if not file or not is_file_allowed(file.filename, {"svg", "pdf"}):
            return "Please upload a valid SVG or PDF file.", 400

        filename, filepath, upload_dir = prepare_upload_path(file.filename, app.root_path)
        clean_upload_dir(upload_dir)
        try:
            save_uploaded_file(file, filepath)
        except ValueError:
            return "Unsupported file type", 400
        print(f"Uploaded filename: {filename}")
        try:
            summary, svg_paths = get_summary_svg_paths(
                filepath,
                upload_dir,
                convert_pdf_to_svgs,
                summarize_svg_pattern
            )
        except Exception as e:
            print(f"Error in get_summary_and_svg_paths: {e}")
            return "Failed to process uploaded file", 500
        if filename.lower().endswith(".pdf"):
            trimmed_summary = "\n".join(summary.splitlines()[:10])
            user_meas_str = build_user_meas_str(bust, waist, hips)
            scale_x, scale_y = get_scale_factors(original_size, bust, hips, SIZE_CHART)
            resize_response = get_pattern_parameters(pattern_type, trimmed_summary, user_meas_str, original_size)
            resized_pngs, resized_svgs = generate_scaled(svg_paths, scale_x, scale_y, upload_dir)
            zip_filename, zip_path = zip_pngs(resized_pngs, upload_dir, filename)
            instructions = get_sewing_instructions(pattern_type, user_meas_str)
            save_upload_to_db(
                filename, "pdf", pattern_type, zip_filename,
                bust, waist, hips, safe_float(request.form.get("torso_height")), original_size,
                scale_x, scale_y, resize_response, instructions
            )
            return render_template(
                "upload_result.html",
                **build_render_context(filename, bust, waist, hips, instructions, zip_filename=zip_filename)
            )
        # For gpt
        trimmed_summary, user_meas_str, scale_x, scale_y, resize_response = prepare_resize_params(
            summary, bust, waist, hips, original_size, pattern_type, SIZE_CHART
        )
        # Parse scale factors
        scale_x = scale_y = 1.0
        for line in resize_response.splitlines():
            if "scale_x" in line:
                scale_x = float(line.split("=", 1)[1].strip())
            if "scale_y" in line:
                scale_y = float(line.split("=", 1)[1].strip())
        if scale_y == 1.0:
            vertical = safe_float(request.form.get("torso_height"))
            base_vertical = 30
            if vertical and base_vertical:
                scale_y = vertical / base_vertical
        scaled_svg, output_path = scale_and_save_svg(filepath, filename, scale_x, scale_y)
        # For gemini
        instructions = get_sewing_instructions(pattern_type, user_meas_str)
        save_upload_to_db(
            filename, "svg", pattern_type, None,
            bust, waist, hips, safe_float(request.form.get("torso_height")), original_size,
            scale_x, scale_y, resize_response, instructions
        )
        print(f"Received pattern_type: {pattern_type}")
        print("Download filename:", filename)
        return render_template(
            "upload_result.html",
            bust=bust,
            waist=waist,
            hips=hips,
            scaled_svg=scaled_svg,
            filename=filename,
            instructions=instructions,
            zipfile=None
        )

    return render_template("upload.html")


@app.route("/download/<filename>")
def download_scaled(filename):
    scaled_dir = os.path.join(os.path.dirname(app.root_path), "scaled")
    return send_from_directory(scaled_dir, filename, as_attachment=True)


@app.route("/generate", methods = ["POST"])
def generate():
    """
    Generate a pattern SVG (e.g., bikini top/bottom) based on user input and AI logic.
    """
    pattern_type = request.form["pattern"]

    if pattern_type == "bikini_top":
        bust_str = request.form.get("bust", "").strip()
        if not bust_str:
            return "Error: Bust measurement is required for bikini top.", 400
        bust = float(bust_str)
        user_meas_str = f"bust = {bust}"
        ai_response = generate_pattern_params_bikini_top(user_measurements=user_meas_str)
        try:
            dims = parse_dimensions(ai_response, ["width", "height"])
            width = dims["width"]
            height = dims["height"]
            svg = generate_bikini_top(width, height)
        except Exception as e:
            return f"Error parsing AI response: {e}", 500

    elif pattern_type == "bikini_bottom":
        waist_str = request.form.get("waist","").strip()
        if not waist_str:
            return "Error: Waist measurement is required for bikini bottom.", 400
        waist = float(waist_str)
        ai_response = generate_pattern_params_bikini_bottom(user_measurements=waist)
        try:
            dims = parse_dimensions(ai_response, ["width", "height"])
            width = dims["width"]
            height = dims["height"]

            svg = generate_bikini_bottom(width, height)

        except Exception as e:
            return f"Error parsing AI response: {e}", 500
    else:
        svg = "<p>Invalid pattern</p>"
    print("Rendering SVG:", svg[:200])
    return render_template("result.html", svg = svg)
