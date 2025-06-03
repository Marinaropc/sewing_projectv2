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