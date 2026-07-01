from utils.report_generator import generate_pdf_report

sample_md = "# Test Report\n\n## Introduction\nThis is a test.\n\n## Conclusion\nIt works!"
generate_pdf_report(sample_md, "test_output.pdf")