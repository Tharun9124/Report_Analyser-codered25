class DataCleaningAgent:
    def __init__(self):
        pass

    def clean(self, data):
        data = data.fillna(method="ffill").fillna(method="bfill")
        return data
