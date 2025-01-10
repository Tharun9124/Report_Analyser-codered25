import pandas as pd

class DataExtractionAgent:
    def __init__(self, input_file):
        self.input_file = input_file

    def extract(self):
        try:
            # Try different encodings and delimiters
            try:
                data = pd.read_csv(self.input_file, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    data = pd.read_csv(self.input_file, encoding="ISO-8859-1")
                except:
                    data = pd.read_csv(self.input_file, encoding="latin1")
            except pd.errors.EmptyDataError:
                raise Exception("The CSV file is empty")
            
            # Basic data validation
            if data.empty:
                raise Exception("No data found in the CSV file")
            
            # Get basic information about the dataset
            self.num_rows = len(data)
            self.num_cols = len(data.columns)
            self.columns = list(data.columns)
            
            return data

        except Exception as e:
            raise Exception(f"Error extracting data: {str(e)}")
