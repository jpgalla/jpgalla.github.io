import sys
import os
from PyPDF2 import PdfReader
import openai

# -------------------------------
# 0. Load OpenAI API key
# -------------------------------
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY not set in environment")
    sys.exit(1)

# -------------------------------
# 1. Parse command line arguments
# -------------------------------
if len(sys.argv) < 3:
    print("Usage: pdf_to_html.py <input.pdf> <file.html>")
    sys.exit(1)

pdf_file = sys.argv[1]
html_file = sys.argv[2]

# -------------------------------
# 2. Extract text from PDF
# -------------------------------
reader = PdfReader(pdf_file)
text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# -------------------------------
# 3. Read original HTML file
# -------------------------------
with open(html_file, "r", encoding="utf-8") as f:
    original_html = f.read()

# -------------------------------
# 4. Build prompt for OpenAI
# -------------------------------
prompt = f"""
You are given a CV in HTML format and new content extracted from a PDF file.

Original HTML:
{original_html[:3000]}

PDF text:
{text[:3000]}

Update the HTML to update the PDF content in the "const cvInteraction" section.
Return the **entire HTML file** updated, not just the snippet.
Do not add explanations, comments, or markdown.
"""

# -------------------------------
# 5. Call OpenAI (modern SDK)
# -------------------------------
client = openai.OpenAI(api_key=openai_api_key)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert in writing professional CVs in HTML format."},
        {"role": "user", "content": prompt}
    ],
    temperature=0
)

# Get the full updated HTML
updated_html = response.choices[0].message.content.strip()

# -------------------------------
# 6. Write updated HTML back to file
# -------------------------------
with open(html_file, "w", encoding="utf-8") as f:
    f.write(updated_html)

print(f"✅ HTML file '{html_file}' updated successfully.")