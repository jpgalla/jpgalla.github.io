import sys
import os
import re
from PyPDF2 import PdfReader
from openai import OpenAI

# -------------------------------
# 0. Load OpenAI API key from environment
# -------------------------------
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY not set in environment")
    sys.exit(1)

client = OpenAI(api_key=openai_api_key)

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
# 3. Build prompt for OpenAI
# -------------------------------
prompt = f"""
You are given the text extracted from a PDF file. 
Using this text, generate **HTML content** that should repupdate  
the content inside the "const cvInteraction" section 
of an existing CV HTML file.

PDF text:
{text[:3000]}
"""

# -------------------------------
# 4. Call OpenAI Chat Completions (new API >=1.0.0)
# -------------------------------
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert in writing professional CVs in HTML format."},
        {"role": "user", "content": prompt}
    ],
    temperature=0
)

# Extract the generated HTML snippet
new_section = response.choices[0].message.content.strip()

# -------------------------------
# 5. Read original HTML
# -------------------------------
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# -------------------------------
# 6. Replace <div id="cvInteraction"> content
# -------------------------------
pattern = re.compile(r'(<div id="cvInteraction">)(.*?)(</div>)', re.DOTALL)
updated_html = re.sub(pattern, r"\1\n" + new_section + r"\n\3", html_content)

# -------------------------------
# 7. Save updated HTML
# -------------------------------
with open(html_file, "w", encoding="utf-8") as f:
    f.write(updated_html)

print("✅ cvInteraction section updated successfully.")
