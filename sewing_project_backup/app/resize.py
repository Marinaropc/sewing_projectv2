def add_reference_line(draw, tile_size):
    from PIL import ImageFont

    line_length_cm = 3
    dpi = 300
    pixels_per_cm = dpi / 2.54
    line_length_px = int(line_length_cm * pixels_per_cm)
    padding = 100

    start_x = tile_size[0] - line_length_px - padding
    start_y = tile_size[1] - padding
    end_x = start_x + line_length_px
    end_y = start_y

    draw.line([(start_x, start_y), (end_x, end_y)], fill="black", width=5)

    try:
        font = ImageFont.truetype("Arial.ttf", 32)
    except IOError:
        font = ImageFont.load_default()

    draw.text((start_x, start_y - 40), f"{line_length_cm} cm", fill="black", font=font)
import xml.etree.ElementTree as Et
from PIL import Image, ImageDraw
from pdf2image import convert_from_path
import os
from pathlib import Path


def convert_pdf_to_images(pdf_path, output_folder):
    images = convert_from_path(pdf_path, dpi=300)
    image_paths = []
    for idx, img in enumerate(images):
        image_filename = f"page_{idx+1}.png"
        image_path = os.path.join(output_folder, image_filename)
        img.save(image_path, "PNG")
        image_paths.append(image_path)
    return image_paths


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def scale_svg(svg_content, scale_x=1.0, scale_y=1.0):
    from .pattern_generator import strip_svg_namespace
    tree = Et.fromstring(svg_content)
    g = Et.Element('g')
    g.attrib['transform'] = f'scale({scale_x},{scale_y})'

    for elem in list(tree):
        g.append(elem)
        tree.remove(elem)

    tree.append(g)
    strip_svg_namespace(tree)
    return Et.tostring(tree, encoding='unicode')


def resize_image(image_path, output_img, scale_x=1.0, scale_y=1.0):
    img = Image.open(image_path)
    new_width = int(img.width * scale_x)
    new_height = int(img.height * scale_y)
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    img_resized.save(output_img)


def tile_image_to_a4(image_path, output_dir):
    from PIL import Image
    import math
    import os

    a4_width_px = 2480  # A4 at 300 DPI
    a4_height_px = 3508

    image = Image.open(image_path)
    image_width, image_height = image.size

    # Calculate number of tiles needed
    cols = math.ceil(image_width / a4_width_px)
    rows = math.ceil(image_height / a4_height_px)

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    tiled_paths = []

    for row in range(rows):
        for col in range(cols):
            left = col * a4_width_px
            upper = row * a4_height_px
            right = min(left + a4_width_px, image_width)
            lower = min(upper + a4_height_px, image_height)

            tile = image.crop((left, upper, right, lower))

            # Add white background if tile is smaller than A4
            if tile.size != (a4_width_px, a4_height_px):
                background = Image.new("RGB", (a4_width_px, a4_height_px), (255, 255, 255))
                background.paste(tile, (0, 0))
                tile = background

            # Draw the reference line on the tile
            draw = ImageDraw.Draw(tile)
            add_reference_line(draw, tile.size)

            tile_filename = f"{base_name}_tile_r{row}_c{col}.png"
            tile_path = os.path.join(output_dir, tile_filename)
            tile.save(tile_path, "PNG")
            tiled_paths.append(tile_path)

    return tiled_paths




def images_to_pdf(image_paths, output_pdf_path):
    images = [Image.open(p).convert("RGB") for p in image_paths]
    images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
