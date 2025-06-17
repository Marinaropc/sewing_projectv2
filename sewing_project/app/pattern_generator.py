"""
Generates SVG patterns for bikini tops and bottoms based on given measurements.
"""
import svgwrite

def generate_bikini_top(width, height, path_logic=None):
    """
    Generate an SVG for a bikini top using simple geometric shapes.
    Draws two triangle cups and vertical straps.
    """
    svg = svgwrite.Drawing(size=("400mm", "400mm"))
    # Draw two triangle cups for the bikini top
    left_top_x = 10 + width * 0.1
    left_top_y = 10 + height * 0.2
    left_base_left_x = 10
    left_base_left_y = 10 + height
    left_base_right_x = 10 + width * 0.2
    left_base_right_y = 10 + height

    right_top_x = 10 + width * 0.3
    right_top_y = 10 + height * 0.2
    right_base_left_x = 10 + width * 0.2
    right_base_left_y = 10 + height
    right_base_right_x = 10 + width * 0.4
    right_base_right_y = 10 + height

    path_data = (
        f"M {left_base_left_x} {left_base_left_y} "
        f"L {left_top_x} {left_top_y} "
        f"L {left_base_right_x} {left_base_right_y} Z "
        f"M {right_base_left_x} {right_base_left_y} "
        f"L {right_top_x} {right_top_y} "
        f"L {right_base_right_x} {right_base_right_y} Z "
        f"M {left_top_x} {left_top_y} "
        f"L {left_top_x} {left_top_y - height * 0.2} "
        f"M {right_top_x} {right_top_y} "
        f"L {right_top_x} {right_top_y - height * 0.2}"
    )
    path = svg.path(d=path_data, fill="none", stroke="black", stroke_width=1.5)
    svg.add(path)
    return svg.tostring()


def generate_bikini_bottom(width: float, height: float) -> str:
    """Generate SVG for bikini bottom pattern based on width and height."""
    svg = svgwrite.Drawing(size=("400mm", "400mm"))

    top_width = width
    crotch_width = width * 0.3
    top_y = 10
    crotch_y = top_y + height * 1.0
    extended_crotch_y = crotch_y + height * 2.0

    # Back panel
    left_top = (10, top_y)
    right_top = (10 + top_width, top_y)
    left_crotch = (10 + (top_width - crotch_width) / 2, crotch_y)
    right_crotch = (10 + (top_width + crotch_width) / 2, crotch_y)

    path_data = (
        f"M {left_top[0]} {left_top[1]} "
        f"C {left_top[0]} {top_y + height * 0.3}, {left_crotch[0]} {crotch_y - height * 0.2}, {left_crotch[0]} {left_crotch[1]} "
        f"L {right_crotch[0]} {right_crotch[1]} "
        f"C {right_crotch[0]} {crotch_y - height * 0.2}, {right_top[0]} {top_y + height * 0.3}, {right_top[0]} {right_top[1]} "
        f"Z"
    )
    # Front panel
    front_top_width = top_width * 0.8
    front_crotch_width = crotch_width * 0.8
    front_left_top = (10 + (top_width - front_top_width) / 2, crotch_y + 20)
    front_right_top = (front_left_top[0] + front_top_width, front_left_top[1])
    front_left_crotch = (10 + (top_width - front_crotch_width) / 2, extended_crotch_y)
    front_right_crotch = (10 + (top_width + front_crotch_width) / 2, extended_crotch_y)
    front_path_data = (
        f"M {front_left_top[0]} {front_left_top[1]} "
        f"C {front_left_top[0]} {front_left_top[1] + height * 0.3}, {front_left_crotch[0]} {front_left_crotch[1] - height * 0.2}, {front_left_crotch[0]} {front_left_crotch[1]} "
        f"L {front_right_crotch[0]} {front_right_crotch[1]} "
        f"C {front_right_crotch[0]} {front_right_crotch[1] - height * 0.2}, {front_right_top[0]} {front_right_top[1] + height * 0.3}, {front_right_top[0]} {front_right_top[1]} "
        f"Z"
    )
    svg.add(svg.path(d=path_data, fill="none", stroke="blue", stroke_width=2))
    svg.add(svg.path(d=front_path_data, fill="none", stroke="blue", stroke_width=2))
    crotch_extension_width = front_right_crotch[0] - front_left_crotch[0]
    crotch_extension_height = height * 0.6
    crotch_extension_x = front_left_crotch[0]
    crotch_extension_y = front_left_crotch[1]
    svg.add(svg.rect(insert=(crotch_extension_x, crotch_extension_y),
                     size=(crotch_extension_width, crotch_extension_height),
                     fill="none", stroke="blue", stroke_width=2))

    return svg.tostring()


def strip_svg_namespace(elem):
    """
    Remove XML namespace from all SVG tags for easier parsing.
    """
    for el in elem.iter():
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]