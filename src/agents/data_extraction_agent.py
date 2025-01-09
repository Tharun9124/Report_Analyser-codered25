import pandas as pd

class DataExtractionAgent:
    def __init__(self, source_path):
        self.source_path = source_path

    def extract(self):
        """
        Extract data from the CSV file at the provided source path.
        """
        try:
            # Try to read the data using 'utf-8' encoding
            data = pd.read_csv(self.source_path, encoding='utf-8')
        except UnicodeDecodeError:
            # If 'utf-8' fails, fall back to 'ISO-8859-1'
            print("Encoding error: Retrying with ISO-8859-1 encoding...")
            data = pd.read_csv(self.source_path, encoding='ISO-8859-1')

        return data
