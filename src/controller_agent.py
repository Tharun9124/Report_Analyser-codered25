from agents.data_extraction_agent import DataExtractionAgent
from agents.data_cleaning_agent import DataCleaningAgent
from agents.analysis_agent import AnalysisAgent

class ControllerAgent:
    def __init__(self, config):
        self.extractor = DataExtractionAgent(config['source_path'])
        self.cleaner = DataCleaningAgent()
        self.analyzer = AnalysisAgent()

    def execute(self):
        """
        Orchestrates the execution of data extraction, cleaning, analysis, and visualization.
        """
        print("Extracting data...")
        raw_data = self.extractor.extract()

        print("Cleaning data...")
        cleaned_data = self.cleaner.clean(raw_data)

        print("Analyzing data...")
        eda_summary, trend_results = self.analyzer.perform_eda(cleaned_data)

        print("Generating plots...")
        pdf_path = self.analyzer.generate_plots(cleaned_data, trend_results)

        # Print the EDA summary (for simplicity in this example)
        print("Exploratory Data Analysis Summary:")
        print(eda_summary)

        print(f"Plots saved to: {pdf_path}")
