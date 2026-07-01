# utils/report_generator.py
# Converts our Markdown research report into a styled, downloadable PDF.
# Auto-detects whether we are running locally (Windows) or on Streamlit Cloud (Linux).

import markdown
import pdfkit
import os
import shutil

# Auto-detect where wkhtmltopdf is installed
def get_wkhtmltopdf_path():
    """Find wkhtmltopdf automatically on any OS."""
    # Try system PATH first (works on Linux/Streamlit Cloud)
    system_path = shutil.which("wkhtmltopdf")
    if system_path:
        return system_path

    # Fallback: Windows default install location
    windows_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if os.path.exists(windows_path):
        return windows_path

    return None


# Basic CSS so the PDF looks clean and professional
REPORT_CSS = """
<style>
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #222;
        padding: 30px;
        max-width: 800px;
        margin: 0 auto;
    }
    h1 { color: #1a4d8f; border-bottom: 2px solid #1a4d8f; padding-bottom: 8px; }
    h2 { color: #2c6cb5; margin-top: 25px; }
    h3 { color: #3a7fc1; }
    li { margin-bottom: 6px; }
    a { color: #1a4d8f; }
    p { margin-bottom: 12px; }
</style>
"""


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown text into full styled HTML."""
    body_html = markdown.markdown(markdown_text, extensions=["extra"])
    full_html = f"<html><head>{REPORT_CSS}</head><body>{body_html}</body></html>"
    return full_html


def generate_pdf_report(markdown_text: str, output_path: str = "report.pdf") -> str:
    """
    Converts markdown -> styled HTML -> PDF.
    Returns the output_path if successful, or None if it failed.
    """
    try:
        wkhtmltopdf_path = get_wkhtmltopdf_path()

        if not wkhtmltopdf_path:
            print("⚠️ wkhtmltopdf not found. Falling back to Markdown.")
            return None

        html_content = markdown_to_html(markdown_text)
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        options = {
            "encoding": "UTF-8",
            "enable-local-file-access": None,
        }

        pdfkit.from_string(html_content, output_path, configuration=config, options=options)
        print(f"✅ PDF saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return None


def generate_markdown_file(markdown_text: str, output_path: str = "report.md") -> str:
    """Fallback: save as plain Markdown file (always works, no dependencies)."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"✅ Markdown saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Markdown save failed: {e}")
        return None