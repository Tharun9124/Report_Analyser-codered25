import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Dict, List
import logging
import io
import base64

class VisualizationAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Use a built-in matplotlib style
        plt.style.use('bmh')
        sns.set_theme(style="whitegrid")
        
    def generate_quick_visualizations(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generate quick visualizations and return them as base64 strings"""
        try:
            visualizations = {}
            
            # 1. Generate distribution plots for numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns[:3]  # Limit to first 3
            if len(numeric_cols) > 0:
                fig, ax = plt.subplots(figsize=(10, 5))
                for col in numeric_cols:
                    sns.kdeplot(data=df[col].dropna(), label=col, ax=ax)
                plt.title('Distribution of Key Numeric Variables')
                plt.legend()
                visualizations['distributions'] = self._fig_to_base64(fig)
                plt.close(fig)
            
            # 2. Generate correlation heatmap
            if len(numeric_cols) > 1:
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', ax=ax)
                plt.title('Correlation Heatmap')
                visualizations['correlation'] = self._fig_to_base64(fig)
                plt.close(fig)
            
            # 3. Generate bar plot for categorical columns
            categorical_cols = df.select_dtypes(include=['object']).columns[:2]  # Limit to first 2
            for col in categorical_cols:
                fig, ax = plt.subplots(figsize=(8, 5))
                df[col].value_counts().head(5).plot(kind='bar', ax=ax)
                plt.title(f'Top 5 Categories in {col}')
                plt.xticks(rotation=45)
                visualizations[f'categorical_{col}'] = self._fig_to_base64(fig)
                plt.close(fig)
            
            return visualizations
            
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {str(e)}")
            return {}
    
    def generate_report_plots(self, df: pd.DataFrame) -> List[str]:
        """Generate plots for PDF report and save them to disk"""
        try:
            output_dir = os.path.join(os.getcwd(), 'output', 'plots')
            os.makedirs(output_dir, exist_ok=True)
            plot_paths = []
            
            # 1. Distribution plot
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns[:3]
            if len(numeric_cols) > 0:
                plt.figure(figsize=(10, 5))
                for col in numeric_cols:
                    sns.kdeplot(data=df[col].dropna(), label=col)
                plt.title('Distribution of Key Variables')
                plt.legend()
                path = os.path.join(output_dir, 'distributions.png')
                plt.savefig(path, bbox_inches='tight', dpi=300)
                plt.close()
                plot_paths.append(path)
            
            # 2. Correlation heatmap
            if len(numeric_cols) > 1:
                plt.figure(figsize=(8, 6))
                sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')
                plt.title('Correlation Analysis')
                path = os.path.join(output_dir, 'correlation.png')
                plt.savefig(path, bbox_inches='tight', dpi=300)
                plt.close()
                plot_paths.append(path)
            
            return plot_paths
            
        except Exception as e:
            self.logger.error(f"Error generating report plots: {str(e)}")
            return []
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
