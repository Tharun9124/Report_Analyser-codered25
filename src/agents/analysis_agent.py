import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class AnalysisAgent:
    def __init__(self):
        pass

    def perform_eda(self, data):
        """
        Perform exploratory data analysis (EDA) on the data.
        """
        eda_summary = {}

        # 1. Summary statistics
        eda_summary['summary'] = data.describe()

        # 2. Check for correlations (only numeric columns)
        numeric_data = data.select_dtypes(include=['number'])
        correlations = numeric_data.corr()
        eda_summary['correlations'] = correlations

        # 3. Trend Analysis (assuming the target column is numeric)
        # Assuming the last column is the target column and dates are in the first column
        trend_results = self.analyze_trends(data)

        return eda_summary, trend_results

    def analyze_trends(self, data):
        """
        Analyze trends over time (e.g., using moving averages).
        """
        trend_results = {}
        
        # Assuming 'Date' is the first column and 'Value' is the target column
        trend_results['dates'] = data.iloc[:, 0]  # Assuming dates are in the first column
        trend_results['values'] = data.iloc[:, -1]  # Assuming target values are in the last column

        return trend_results

    def generate_plots(self, data, trend_results):
        """
        Generate and save plots to a PDF file.
        """
        pdf_path = "output_plots.pdf"
        num_plots = 4  # Adjust based on how many plots you want to create
        num_rows = (num_plots // 2) + (num_plots % 2)

        with PdfPages(pdf_path) as pdf:
            # Generate plots for EDA results
            for i in range(num_plots):
                plt.subplot(num_rows, 2, i + 1)
                plt.plot(trend_results['dates'], trend_results['values'])
                plt.title(f'Trend Plot {i + 1}')
                plt.xlabel('Date')
                plt.ylabel('Value')

            # Save all plots to the PDF
            pdf.savefig()  # Save the current figure to PDF
            plt.close()  # Close the plot to avoid memory issues

        return pdf_path
