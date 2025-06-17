import os
import openai
from dotenv import load_dotenv


load_dotenv()
SIZE_CHART = {
    "32": {"bust": 76, "waist": 60, "hips": 84},
    "34": {"bust": 80, "waist": 64, "hips": 88},
    "36": {"bust": 84, "waist": 68, "hips": 92},
    "38": {"bust": 88, "waist": 72, "hips": 96},
    "40": {"bust": 92, "waist": 76, "hips": 100},
    "42": {"bust": 96, "waist": 80, "hips": 104},
    "44": {"bust": 100, "waist": 84, "hips": 108},
    "46": {"bust": 104, "waist": 88, "hips": 112},
    "48": {"bust": 110, "waist": 94, "hips": 118}
}
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_pattern_parameters(pattern_type, svg_summary, user_measurements, original_size=None):
    """
    Ask ChatGPT to estimate the original pattern size and return scale factors based on user measurements.
    Returns the AI's raw response with estimated size and scaling.
    """

    prompt = f"""
    You are a pattern-resizing assistant.
    
    Here is a simplified summary of the uploaded {pattern_type} SVG pattern:
    {svg_summary}
    
    The user’s measurements are:
    {user_measurements}
    """
    if original_size:
        prompt += ( f"Some patterns may have many sizes in them, user will select their original size"
                   f"\nThe pattern is originally designed for size {original_size}.")

    prompt += """
    First estimate the pattern’s original size (e.g. bust, waist, or hips).
    Then compute how much to scale the X and Y axes so the pattern matches the user’s measurements.
    Respond *exactly* in this format (no extra text):
    
    estimated_bust = <number>
    estimated_waist = <number>
    estimated_hips = <number>
    scale_x = <number>
    scale_y = <number>
    """

    client = openai.OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.3
    )

    return response.choices[0].message.content


def generate_pattern_params_bikini_top(user_measurements):
    """
    Ask ChatGPT to generate SVG path dimensions and logic for a bikini top based on user measurements.
    """

    prompt = f"""
    You are a sewing pattern generator assistant. Your task is to generate SVG path logic for a bikini top pattern based on user measurements.

    User measurements:
    {user_measurements}

    Rules:
    - NO extra text or explanation
    - Use only SVG path commands: M, L, C, Z
    - Ensure the shape resembles a realistic bikini top

    Output exactly in this example format (no extra lines or comments):
    width = 140
    height = 100
    path_logic = SVG path commands

    IMPORTANT:
    Respond with all 3 lines exactly as shown above. Do not skip any of them. Do not use Markdown.
    """
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.4
    )
    return response.choices[0].message.content


def generate_pattern_params_corset(user_measurements):
    """
    Ask ChatGPT to generate a fitted corset SVG path using user body measurements.
    Includes shaping for bust, waist, and hips.
    """
    prompt = f"""
    You are a pattern design assistant. Generate a realistic SVG path for a corset pattern based on the user’s 
    measurements.

    User measurements:
    {user_measurements}

    This is for a sewing pattern generator app. The shape should include:
    - A fitted design that contours the bust, waist, and hips
    - Multiple vertical panels or symmetrical halves for shaping
    - Use SVG path logic (e.g., Bézier curves) to create smooth curves and tapering seams
    - Defined waist cinch and possible bust shaping
    - Optional indications of boning channels and seam allowances
    - Avoid simple rectangles or shapeless outlines
    Use multiple vertical panels, drawn side-by-side (not overlapping).
    The shape should taper at the waist and expand at bust and hips.
    Respond with a continuous SVG path that approximates one half of the corset body (the other half can be mirrored).
    Only reply in this EXACT format:
    width = <number>
    height = <number>
    path_logic = M 10 10 C 30 30, 50 10, 70 20 ...
    Make sure path_logic is a real string of SVG path data.
    """
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.4
    )
    return response.choices[0].message.content


def generate_pattern_params_bikini_bottom(user_measurements):
    """
    Ask ChatGPT to generate SVG path info for a bikini bottom, shaped to user hip and waist curves.
    """


    prompt = f"""
    You are a pattern design assistant. Generate a realistic SVG path for a bikini bottom pattern based on the user’s 
    measurements.

    User measurements:
    {user_measurements}

    This is for a sewing pattern generator app. The shape should include:
    - A front and back panel or a symmetrical shape for simplicity
    - Natural curves that follow hip and crotch contours
    - Use SVG path logic (e.g., Bézier curves) for smooth shaping
    - Defined waist and leg openings
    - Optional seam allowance and dart hints
    - Avoid plain geometric shapes or unrealistic straight lines
    Shape should resemble an hourglass with top waist and lower leg openings.
    Return a single path that outlines the full front panel.
    Only reply in this EXACT format:
    width = <number>
    height = <number>
    path_logic = M 10 10 C 30 30, 50 10, 70 20 ...
    Make sure path_logic is a real string of SVG path data.
    """
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.4
    )
    return response.choices[0].message.content
