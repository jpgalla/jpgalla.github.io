import sys
import os
import re
from PyPDF2 import PdfReader
import openai

# Load OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check arguments: we expect a PDF input and an HTML file to update
if len(sys.argv) < 3:
    print("Usage: pdf_to_html.py <input.pdf> <file.html>")
    sys.exit(1)

pdf_file = sys.argv[1]
html_file = sys.argv[2]

# --------------------------------------------------
# 1. Extract text from the PDF
# --------------------------------------------------
reader = PdfReader(pdf_file)
text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# --------------------------------------------------
# 2. Build prompt for OpenAI
# --------------------------------------------------
prompt = f"""
You are given the text extracted from a PDF file.
Using this text, generate **HTML content** that should update
the content inside the "const cvInteraction" section
of an existing CV HTML file.

PDF text:
{text[:3000]}
"""

# --------------------------------------------------
# 3. Call OpenAI API
# --------------------------------------------------
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",  # you can change to gpt-4o, gpt-4.1, etc.
    messages=[
        {"role": "system", "content": "You are an expert in writing professional CVs in HTML format."},
        {"role": "user", "content": prompt}
    ],
    temperature=0
)

# Extract model output (the new HTML snippet)
new_section = response["choices"][0]["message"]["content"].strip()

# --------------------------------------------------
# 4. Read the original HTML file
# --------------------------------------------------
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# --------------------------------------------------
# 5. Replace only the content of <div id="cvInteraction"> ... </div>
# --------------------------------------------------
pattern = re.compile(r'(<div id="cvInteraction">)(.*?)(</div>)', re.DOTALL)
updated_html = re.sub(pattern, r"\1\n" + new_section + r"\n\3", html_content)

# --------------------------------------------------
# 6. Save updated HTML file
# --------------------------------------------------
with open(html_file, "w", encoding="utf-8") as f:
    f.write(updated_html)

print("✅ cvInteraction section updated successfully.")

