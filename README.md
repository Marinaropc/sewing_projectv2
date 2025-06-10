Sewing Pattern Resizer & Tiler

This app allows users to upload sewing patterns (in PDF or SVG format), resizes them according to custom body measurements, and outputs printable A4-tiled PNG and PDF versions. Perfect for home sewists with custom sizing needs!

Features
	•	Upload patterns as PDF or SVG
	•	Resize based on user-provided body measurements
	•	Automatically convert and tile resized patterns to A4 sheets
	•	Download as a zipped PNG set or combined PDF
	•	Scale ruler included to verify print accuracy

How It Works
	1.	Upload: Users upload PDF or SVG patterns.
	2.	Convert: PDFs are converted to SVG using Inkscape.
	3.	Resize: Patterns are scaled according to user input.
	4.	Render: SVGs are rendered to PNG.
	5.	Tile: Images are tiled into A4-sized segments, padded with whitespace if needed.
	6.	Download: A ZIP file with all A4 pages will be generated, along with an optional combined PDF.

Technologies Used
	•	Python
	•	Flask (backend server)
	•	Pillow (image processing)
	•	pdf2image & Inkscape (PDF to image/SVG conversion)
	•	xml.etree.ElementTree (SVG manipulation)

Requirements
	•	Python 3.8+
	•	Inkscape (must be installed and in system PATH)

Install Python Dependencies
	•	pip install -r requirements.txt

Usage

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your browser and go to:
   ```
   http://localhost:5000
   ```

3. Upload your pattern file (SVG or PDF).
4. Enter your body measurements (e.g., waist, hips).
5. Submit and wait for the file processing.
6. Download your resized and A4-tiled sewing pattern as a ZIP file.

Notes
- If uploading a PDF, each page will be converted to an SVG before resizing.
- A 5 cm reference line will be added to each output image to verify scaling.
- Output images are automatically tiled to A4 paper size with padding if needed.
