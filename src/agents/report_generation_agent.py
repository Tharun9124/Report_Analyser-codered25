import os

class ReportGenerationAgent:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate(self, analysis_results):
        report_path = os.path.join(self.output_dir, 'report.txt')
        with open(report_path, 'w') as file:
            file.write("Analysis Results:\n")
            file.write(str(analysis_results))
        print(f"Report generated at: {report_path}")
