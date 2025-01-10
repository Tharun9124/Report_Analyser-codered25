import pandas as pd
import google.generativeai as genai
from typing import Dict, Any, List
import json
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix
import numpy as np

class MedicalLLMAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Configure the generative AI
        genai.configure(api_key='AIzaSyAFE1w3E3ui6EKq3duWq6YkceeBFdXm4g0')
        self.model = genai.GenerativeModel('gemini-pro')

    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """Prepare a summary of the dataset for the AI model"""
        summary = f"""
        Dataset Overview:
        - Total Records: {len(df)}
        - Features: {len(df.columns)}
        - Numeric Features: {len(df.select_dtypes(include=['int64', 'float64']).columns)}
        - Categorical Features: {len(df.select_dtypes(include=['object']).columns)}
        
        Feature Names: {', '.join(df.columns)}
        
        Basic Statistics:
        {df.describe().to_string()}
        
        Missing Values:
        {df.isnull().sum().to_dict()}
        """
        return summary

    def _train_prediction_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train a simple prediction model on the data"""
        try:
            # Identify potential target variables (categorical columns with few unique values)
            categorical_cols = df.select_dtypes(include=['object']).columns
            potential_targets = [col for col in categorical_cols if df[col].nunique() < 10]
            
            if not potential_targets:
                return {}
            
            # Select the first potential target
            target_col = potential_targets[0]
            
            # Prepare features (numeric columns only for simplicity)
            feature_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(feature_cols) == 0:
                return {}
                
            X = df[feature_cols]
            
            # Encode target variable
            le = LabelEncoder()
            y = le.fit_transform(df[target_col])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Make predictions
            predictions = model.predict(X_test)
            
            # Calculate accuracy
            acc = accuracy_score(y_test, predictions)
            
            # Create confusion matrix
            cm = confusion_matrix(y_test, predictions)
            
            return {
                'target_column': target_col,
                'feature_columns': list(feature_cols),
                'predictions': predictions.tolist(),
                'actual': y_test.tolist(),
                'classes': le.classes_.tolist(),
                'accuracy': acc,
                'confusion_matrix': cm.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Error in prediction model: {str(e)}")
            return {}

    def analyze(self, df: pd.DataFrame, analysis_type: str = "basic") -> Dict[str, Any]:
        """Analyze the medical data and generate insights"""
        try:
            # Prepare data summary
            data_summary = self._prepare_data_summary(df)
            
            # Initialize prediction_results
            prediction_results = {}
            
            # Create appropriate prompt based on analysis type
            if analysis_type == "basic":
                prompt = f"""
                Analyze this medical dataset and provide insights. Use this data summary:
                {data_summary}
                
                Return a JSON with these sections:
                {{
                    "summary": "A comprehensive overview paragraph",
                    "insights": [4-5 key insights about the data],
                    "risk_factors": [3-4 identified risk factors],
                    "recommendations": [3-4 actionable recommendations],
                    "statistical_notes": [2-3 important statistical observations]
                }}
                """
            else:  # Detailed Analysis with Predictions
                # Train prediction model
                prediction_results = self._train_prediction_model(df)
                
                prompt = f"""
                Perform a detailed analysis of this medical dataset including predictive insights. Use this data:
                {data_summary}
                
                Additional Context:
                - Prediction Target: {prediction_results.get('target_column', 'None')}
                - Features Used: {prediction_results.get('feature_columns', [])}
                
                Return a JSON with these sections:
                {{
                    "summary": "A comprehensive overview paragraph",
                    "insights": [5-6 detailed insights about the data],
                    "risk_factors": [4-5 identified risk factors],
                    "recommendations": [4-5 detailed actionable recommendations],
                    "statistical_notes": [3-4 important statistical observations],
                    "predictive_insights": [2-3 insights about the predictive analysis]
                }}
                """

            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            try:
                # Extract JSON from response
                response_text = response.text
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                json_str = response_text[start_idx:end_idx]
                analysis_results = json.loads(json_str)
                
                # Add prediction results if available
                if prediction_results:
                    analysis_results.update(prediction_results)
                
                return analysis_results
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON response: {str(e)}")
                return {
                    "error": "Failed to parse AI response",
                    "raw_response": response.text
                }
                
        except Exception as e:
            self.logger.error(f"Error in analyze method: {str(e)}")
            return {
                "error": str(e),
                "details": "Failed to analyze data"
            }
