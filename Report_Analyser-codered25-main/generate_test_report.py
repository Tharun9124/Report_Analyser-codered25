import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

# Create sample data
data = {
    'Year': [2020, 2021, 2022, 2023, 2024],
    'Sales': [100, 150, 200, 250, 300],
    'Profit': [20, 30, 40, 50, 60],
    'Category': ['A', 'B', 'A', 'C', 'B']
}

df = pd.DataFrame(data)

# Create output directory if it doesn't exist
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Generate PDF
pdf_path = os.path.join(output_dir, 'test_report.pdf')

try:
    with PdfPages(pdf_path) as pdf:
        # Plot 1: Line plot
        plt.figure(figsize=(10, 6))
        plt.plot(df['Year'], df['Sales'], marker='o', label='Sales')
        plt.plot(df['Year'], df['Profit'], marker='s', label='Profit')
        plt.title('Sales and Profit Over Time')
        plt.xlabel('Year')
        plt.ylabel('Amount')
        plt.legend()
        plt.grid(True)
        pdf.savefig()
        plt.close()

        # Plot 2: Bar plot
        plt.figure(figsize=(10, 6))
        category_counts = df['Category'].value_counts()
        plt.bar(category_counts.index, category_counts.values)
        plt.title('Distribution by Category')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.grid(True)
        pdf.savefig()
        plt.close()

    print(f"PDF report generated successfully at: {pdf_path}")
    print("Please check the output directory for test_report.pdf")

except Exception as e:
    print(f"Error generating PDF: {str(e)}")
