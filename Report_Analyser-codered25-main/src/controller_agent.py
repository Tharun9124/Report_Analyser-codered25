import os
import json
from agents.data_extraction_agent import DataExtractionAgent
from agents.data_cleaning_agent import DataCleaningAgent
from agents.analysis_agent import AnalysisAgent
from agents.visualization_agent import VisualizationAgent
from agents.llm_agent import LLMAgent
from agents.report_generation_agent import ReportGenerationAgent

class ControllerAgent:
    def __init__(self, config):
        self.config = config
        self.extractor = DataExtractionAgent(config["input_file"])
        self.cleaner = DataCleaningAgent()
        self.analyzer = AnalysisAgent()
        self.visualizer = VisualizationAgent(config["output_dir"])
        self.llm = LLMAgent(config["google_api_key"])
        self.reporter = ReportGenerationAgent(config["output_dir"])

    def execute(self):
        # Step 1: Extract data
        data = self.extractor.extract()

        # Step 2: Clean data
        cleaned_data = self.cleaner.clean(data)

        # Step 3: Analyze data
        summary, trends = self.analyzer.analyze(cleaned_data)

        # Step 4: Generate insights
        insights = self.llm.generate_insights(summary, trends)

        # Step 5: Create visualizations
        pdf_path = self.visualizer.create_visualizations(cleaned_data, trends)

        # Step 6: Generate report
        report_path = self.reporter.generate_report(summary, trends, insights, pdf_path)

        print(f"Report generated: {report_path}")
