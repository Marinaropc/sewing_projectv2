from flask import Flask, render_template, request, send_from_directory
from .ai_calls import get_pattern_parameters, SIZE_CHART
from .pattern_generator import generate_bikini_top, generate_corset, generate_bikini_bottom
import os
from .gemini_calls import get_sewing_instructions
from werkzeug.utils import secure_filename
from .pdf_to_svg import convert_pdf_to_svgs
from .svg_extract import summarize_svg_pattern
from .resize import safe_float, scale_svg, resize_image, tile_image_to_a4
import subprocess

app = Flask(__name__)

def clean_upload_dir(upload_dir):
    for root, dirs, files in os.walk(upload_dir):
        for file in files:
            os.remove(os.path.join(root, file))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download_zip/<filename>")
def download_zip(filename):
    zip_dir = os.path.join(app.root_path, "uploads", "resized")
    return send_from_directory(zip_dir, filename, as_attachment=True)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Get pattern type and measurements from user
        pattern_type = request.form.get("pattern")
        bust = safe_float(request.form.get("bust"))
        waist = safe_float(request.form.get("waist"))
        hips = safe_float(request.form.get("hips"))
        original_size = request.form.get("original_size")

        file = request.files.get("svg_file")
        if not file:
            return "Please upload a file.", 400

        filename = secure_filename(file.filename)
        upload_dir = os.path.join(app.root_path, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        clean_upload_dir(upload_dir)
        filepath = os.path.join(upload_dir, filename)
        if filename.lower().endswith(".svg"):
            svg_content = file.read().decode("utf-8")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(svg_content)
        elif filename.lower().endswith(".pdf"):
            file.save(filepath)
        else:
            return "Unsupported file type", 400
        print(f"Uploaded filename: {filename}")
        if filename.lower().endswith(".pdf"):
            try:
                print("✅ Calling convert_pdf_to_svgs...")
                svg_paths = convert_pdf_to_svgs(filepath, os.path.join(upload_dir, "svg_pages"))
                print(f"SVGs generated from PDF: {svg_paths}")
            except Exception as e:
                print(f"❌ Error in convert_pdf_to_svgs: {e}")
                return "Failed to convert PDF to SVG", 500
            summary = summarize_svg_pattern(svg_paths[0]) if svg_paths else "No SVG pages were created."
            trimmed_summary = "\n".join(summary.splitlines()[:10])
            measurements = []
            if bust:
                measurements.append(f"bust = {bust}")
            if waist:
                measurements.append(f"waist = {waist}")
            if hips:
                measurements.append(f"hips = {hips}")
            user_meas_str = ", ".join(measurements)

            scale_x = scale_y = 1.0
            if original_size and original_size in SIZE_CHART:
                original = SIZE_CHART[original_size]
                if bust and original["bust"]:
                    scale_x = bust / original["bust"]
                if hips and original["hips"]:
                    scale_y = hips / original["hips"]

            resize_response = get_pattern_parameters(pattern_type, trimmed_summary, user_meas_str, original_size)

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

                # Convert SVG to PNG with Inkscape
                output_png = os.path.splitext(output_svg)[0] + ".png"
                cmd = [
                    "inkscape",
                    output_svg,
                    "--export-area-drawing",
                    "--export-type=png",
                    "--export-filename", output_png
                ]
                try:
                    subprocess.run(cmd, check=True)

                    # Resize PNG before tiling
                    resized_png_path = output_png.replace(".png", "_resized.png")
                    resize_image(output_png, resized_png_path, scale_x=3.0, scale_y=3.0)

                    # Tile the resized PNG, not the original
                    tiled_paths = tile_image_to_a4(resized_png_path, resized_dir)
                    resized_pngs.extend(tiled_paths)
                    print(f"✅ Appending {len(tiled_paths)} tiles for {resized_png_path}")

                    # Remove or comment out the previous tiling call on the original PNG:
                    # tiled_paths = tile_image_to_a4(output_png, resized_dir)
                except Exception as e:
                    print(f"Error converting {output_svg} to PNG: {e}")

            from zipfile import ZipFile

            print(f"🧩 Total PNGs to zip: {len(resized_pngs)}")
            print(f"Files: {resized_pngs}")

            zip_filename = f"resized_{os.path.splitext(filename)[0]}.zip"
            zip_path = os.path.join(resized_dir, zip_filename)

            with ZipFile(zip_path, 'w') as zipf:
                for png_file in resized_pngs:
                    if os.path.exists(png_file):
                        zipf.write(png_file, os.path.basename(png_file))
                    else:
                        print(f"⚠️ Warning: Skipping missing file: {png_file}")
            instructions = get_sewing_instructions(pattern_type, user_meas_str)
            return render_template(
                "upload_result.html",
                zipfile=zip_filename,
                filename=filename,
                bust=bust,
                waist=waist,
                hips=hips,
                instructions=instructions
            )
        # For GPT
        summary = summarize_svg_pattern(filepath)
        trimmed_summary = "\n".join(summary.splitlines()[:10])

        measurements = []
        if bust:
            measurements.append(f"bust = {bust}")
        if waist:
            measurements.append(f"waist = {waist}")
        if hips:
            measurements.append(f"hips = {hips}")

        user_meas_str = ", ".join(measurements)
        # Get GPT resize instructions
        resize_response = get_pattern_parameters(
            pattern_type, trimmed_summary, user_meas_str, original_size
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

        # Apply scaling
        scaled_svg = scale_svg(svg_content, scale_x, scale_y)
        output_path = os.path.join("scaled", f"scaled_{filename}")
        os.makedirs("scaled", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(scaled_svg)

        # For gemini
        instructions = get_sewing_instructions(pattern_type, user_meas_str)
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
    pattern_type = request.form["pattern"]

    if pattern_type == "bikini_top":
        bust_str = request.form.get("bust", "").strip()
        if not bust_str:
            return "Error: Bust measurement is required for bikini top.", 400
        bust = float(bust_str)

        user_meas_str = f"bust = {bust}"
        ai_response = get_pattern_parameters("bikini_top", "simple shape", user_meas_str)

        try:
            for line in ai_response.splitlines():
                if "width" in line and "height" in line:
                    parts = line.replace("**", "").replace("Output:", "").split(",")
                    width = float(parts[0].split("=")[1].strip())
                    height = float(parts[1].split("=")[1].strip())
                    break
            else:
                raise ValueError("No valid line found with width and height")

            svg = generate_bikini_top(width)

        except Exception as e:
            return f"Error parsing AI response: {e}", 500

    elif pattern_type == "bikini_bottom":
        waist_str = request.form.get("waist","").strip()
        if not waist_str:
            return "Error: Waist measurement is required for bikini bottom.", 400
        waist = float(waist_str)
        ai_response = get_pattern_parameters("bikini_bottom", f"waist = {waist}")
        try:
            for line in ai_response.splitlines():
                if "width" in line and "height" in line:
                    parts = line.replace("**", "").replace("Output:", "").split(",")
                    width = float(parts[0].split("=")[1].strip())
                    height = float(parts[1].split("=")[1].strip())
                    break
            else:
                raise ValueError("No valid line found with width and height")

            svg = generate_bikini_bottom(waist)

        except Exception as e:
            return f"Error parsing AI response: {e}", 500

    elif pattern_type == 'corset':
        waist_str = request.form.get('waist', '').strip()
        bust_str = request.form.get('bust', '').strip()
        if not waist_str or not bust_str:
            return "Error: Both waist and bust measurements are required for corset.", 400
        waist = float(waist_str)
        bust = float(bust_str)
        ai_response = get_pattern_parameters("corset", f"waist = {waist}, bust = {bust}")

        try:
            for line in ai_response.splitlines():
                if "top_width" in line and "bottom_width" in line and "height" in line:
                    parts = line.replace("**", "").replace("Output:", "").split(",")
                    top_width = float(parts[0].split("=")[1].strip())
                    bottom_width = float(parts[1].split("=")[1].strip())
                    height = float(parts[2].split("=")[1].strip())
                    break
            else:
                raise ValueError("No valid line found with top_width, bottom_width, and height")

            svg = generate_corset(top_width, bottom_width)

        except Exception as e:
            return f"Error parsing AI response: {e}", 500

    else:
        svg = "<p>Invalid pattern</p>"
    return render_template("result.html", svg = svg)