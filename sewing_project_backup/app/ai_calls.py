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