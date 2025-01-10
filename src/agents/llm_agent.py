import google.generativeai as genai

class LLMAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_insights(self, summary, trends):
        prompt = (
            f"Analyze the following data summary and trends:\n\n"
            f"Summary: {summary}\n"
            f"Trends: {trends}\n\n"
            f"Provide prescriptive insights and actionable recommendations in a clear, professional format."
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error in LLM Agent: {str(e)}")
            return "Unable to generate insights at this time. Please check the data and try again."
