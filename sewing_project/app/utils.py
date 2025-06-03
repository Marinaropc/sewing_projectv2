import os
from werkzeug.utils import secure_filename


def build_user_meas_str(bust, waist, hips):
    measurements = []
    if bust:
        measurements.append(f"bust = {bust}")
    if waist:
        measurements.append(f"waist = {waist}")
    if hips:
        measurements.append(f"hips = {hips}")
    return ", ".join(measurements)


def clean_upload_dir(upload_dir):
    for root, dirs, files in os.walk(upload_dir):
        for file in files:
            os.remove(os.path.join(root, file))


def is_file_allowed(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def prepare_upload_path(raw_filename, root_path):
    filename = secure_filename(raw_filename)
    upload_dir = os.path.join(root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    clean_upload_dir(upload_dir)
    filepath = os.path.join(upload_dir, filename)
    return filename, filepath, upload_dir


def save_uploaded_file(file, filepath):
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
    scale_x = scale_y = 1.0
    if original_size and original_size in size_chart:
        original = size_chart[original_size]
        if bust and original["bust"]:
            scale_x = bust / original["bust"]
        if hips and original["hips"]:
            scale_y = hips / original["hips"]
    return scale_x, scale_y