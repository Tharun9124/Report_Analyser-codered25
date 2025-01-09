class DataCleaningAgent:
    def __init__(self):
        self.fill_method = 'ffill'  # You can choose to use 'bfill' or other methods

    def clean(self, data):
        """
        Perform cleaning tasks on the data.
        """
        # Fill missing values using forward fill method
        data = data.fillna(method=self.fill_method)

        # You can add more cleaning steps here if necessary

        return data
