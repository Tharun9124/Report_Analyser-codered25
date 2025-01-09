from fpdf import FPDF
import os

class PDFReportAgent:
    def __init__(self, output_dir, pdf_file):
        self.output_dir = output_dir
        self.pdf_file = os.path.join(output_dir, pdf_file)
        self.pdf = FPDF()

    def create_report(self, data, analysis_results, visualizations):
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)

        # 1. Dataset Overview
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(200, 10, txt="Dataset Overview", ln=True, align="L")
        self.pdf.set_font("Arial", size=12)
        for col in data.columns:
            self.pdf.cell(200, 10, txt=f"{col}: {data[col].dtype}", ln=True, align="L")

        # 2. Summary Statistics
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(200, 10, txt="Summary Statistics", ln=True, align="L")
        self.pdf.set_font("Arial", size=12)
        for col, stats in analysis_results["Summary Statistics"].items():
            self.pdf.cell(200, 10, txt=f"{col}: {stats}", ln=True, align="L")

        # 3. Trends and Recommendations
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(200, 10, txt="Trends and Recommendations", ln=True, align="L")
        for col, trend in analysis_results["Trends"].items():
            self.pdf.cell(200, 10, txt=f"{col}: {trend}", ln=True, align="L")
        for recommendation in analysis_results["Recommendations"]:
            self.pdf.cell(200, 10, txt=recommendation, ln=True, align="L")

        # 4. Visualizations
        self.pdf.set_font("Arial", style="B", size=14)
        self.pdf.cell(200, 10, txt="Visualizations", ln=True, align="L")
        for name, path in visualizations.items():
            self.pdf.image(path, w=100)

        # Save PDF
        self.pdf.output(self.pdf_file)
