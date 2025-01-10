import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import logging
from typing import Dict, Any
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

class ReportGenerationAgent:
    def __init__(self):
        self.output_dir = 'output/reports'
        self.plots_dir = os.path.join(self.output_dir, 'plots')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.logger = logging.getLogger(__name__)

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=1  # Center alignment
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=20,
            spaceAfter=15,
            textColor=colors.HexColor('#2c3e50')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=16,
            spaceAfter=10,
            textColor=colors.HexColor('#34495e')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            leading=16
        ))

    def _generate_visualizations(self, df: pd.DataFrame) -> dict:
        """Generate visualizations for the report"""
        plot_paths = {}
        
        try:
            # 1. Distribution plots for key numeric features
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns[:4]
            plt.figure(figsize=(12, 8))
            for i, col in enumerate(numeric_cols, 1):
                plt.subplot(2, 2, i)
                sns.histplot(data=df, x=col, kde=True)
                plt.title(f'Distribution of {col}')
            plt.tight_layout()
            dist_path = os.path.join(self.plots_dir, 'distributions.png')
            plt.savefig(dist_path, dpi=300, bbox_inches='tight')
            plt.close()
            plot_paths['distributions'] = dist_path

            # 2. Correlation heatmap
            plt.figure(figsize=(10, 8))
            numeric_df = df.select_dtypes(include=['int64', 'float64'])
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
            plt.title('Feature Correlation Analysis')
            corr_path = os.path.join(self.plots_dir, 'correlation.png')
            plt.savefig(corr_path, dpi=300, bbox_inches='tight')
            plt.close()
            plot_paths['correlation'] = corr_path

            # 3. Box plots for outlier detection
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=df[numeric_cols])
            plt.xticks(rotation=45)
            plt.title('Outlier Analysis')
            box_path = os.path.join(self.plots_dir, 'boxplots.png')
            plt.savefig(box_path, dpi=300, bbox_inches='tight')
            plt.close()
            plot_paths['boxplots'] = box_path

            return plot_paths
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {str(e)}")
            return {}

    def _analyze_predictions(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prediction results if available"""
        prediction_analysis = {}
        
        if 'predictions' in analysis_results:
            predictions = analysis_results['predictions']
            actual = analysis_results.get('actual', None)
            
            if actual is not None:
                # Calculate accuracy
                accuracy = accuracy_score(actual, predictions)
                prediction_analysis['accuracy'] = f"{accuracy:.2%}"
                
                # Generate classification report
                prediction_analysis['classification_report'] = classification_report(actual, predictions)
                
                # Create confusion matrix
                cm = confusion_matrix(actual, predictions)
                plt.figure(figsize=(8, 6))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.title('Confusion Matrix')
                plt.xlabel('Predicted')
                plt.ylabel('Actual')
                cm_path = os.path.join(self.plots_dir, 'confusion_matrix.png')
                plt.savefig(cm_path, dpi=300, bbox_inches='tight')
                plt.close()
                prediction_analysis['confusion_matrix_path'] = cm_path
        
        return prediction_analysis

    def generate_report(self, data_file: str, analysis_results: Dict[str, Any], report_type: str = "detailed") -> str:
        """Generate a comprehensive PDF report with analysis results and visualizations"""
        try:
            # Read the data
            df = pd.read_csv(data_file)
            
            # Generate visualizations
            plot_paths = self._generate_visualizations(df)
            
            # Analyze predictions if available
            prediction_analysis = self._analyze_predictions(analysis_results)
            
            # Create report filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = os.path.join(self.output_dir, f'medical_report_{timestamp}.pdf')
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                report_filename,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the PDF content
            story = []
            
            # Add logo if available
            logo_path = "assets/logo.png"
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=2*inch, height=1*inch)
                story.append(logo)
                story.append(Spacer(1, 20))
            
            # Add title
            story.append(Paragraph("Medical Data Analysis Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Add timestamp and file info
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                 self.styles['CustomBody']))
            story.append(Paragraph(f"Analyzed File: {os.path.basename(data_file)}", 
                                 self.styles['CustomBody']))
            story.append(Spacer(1, 20))
            
            # Add executive summary
            if 'summary' in analysis_results:
                story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
                story.append(Paragraph(analysis_results['summary'], self.styles['CustomBody']))
                story.append(Spacer(1, 20))
            
            # Add data overview
            story.append(Paragraph("Dataset Overview", self.styles['CustomHeading']))
            overview_data = [
                ["Total Records", str(len(df))],
                ["Total Features", str(len(df.columns))],
                ["Numeric Features", str(len(df.select_dtypes(include=['int64', 'float64']).columns))],
                ["Categorical Features", str(len(df.select_dtypes(include=['object']).columns))],
                ["Missing Values", str(df.isnull().sum().sum())]
            ]
            
            overview_table = Table(overview_data, colWidths=[3*inch, 3*inch])
            overview_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f4f6f6')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
            ]))
            story.append(overview_table)
            story.append(Spacer(1, 20))
            
            # Add key insights
            if 'insights' in analysis_results:
                story.append(Paragraph("Key Insights", self.styles['CustomHeading']))
                for insight in analysis_results['insights']:
                    story.append(Paragraph(f"• {insight}", self.styles['CustomBody']))
                story.append(Spacer(1, 20))
            
            # Add visualizations
            if plot_paths:
                story.append(Paragraph("Data Visualizations", self.styles['CustomHeading']))
                
                # Add distribution plots
                if 'distributions' in plot_paths:
                    story.append(Paragraph("Feature Distributions", self.styles['CustomSubHeading']))
                    story.append(Image(plot_paths['distributions'], width=7*inch, height=5*inch))
                    story.append(Spacer(1, 15))
                
                # Add correlation heatmap
                if 'correlation' in plot_paths:
                    story.append(Paragraph("Correlation Analysis", self.styles['CustomSubHeading']))
                    story.append(Image(plot_paths['correlation'], width=7*inch, height=5*inch))
                    story.append(Spacer(1, 15))
                
                # Add box plots
                if 'boxplots' in plot_paths:
                    story.append(Paragraph("Outlier Analysis", self.styles['CustomSubHeading']))
                    story.append(Image(plot_paths['boxplots'], width=7*inch, height=4*inch))
                    story.append(Spacer(1, 20))
            
            # Add prediction analysis if available
            if prediction_analysis:
                story.append(Paragraph("Prediction Analysis", self.styles['CustomHeading']))
                
                if 'accuracy' in prediction_analysis:
                    story.append(Paragraph(f"Model Accuracy: {prediction_analysis['accuracy']}", 
                                        self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
                
                if 'classification_report' in prediction_analysis:
                    story.append(Paragraph("Classification Report", self.styles['CustomSubHeading']))
                    story.append(Paragraph(prediction_analysis['classification_report'], 
                                        self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
                
                if 'confusion_matrix_path' in prediction_analysis:
                    story.append(Paragraph("Confusion Matrix", self.styles['CustomSubHeading']))
                    story.append(Image(prediction_analysis['confusion_matrix_path'], 
                                    width=6*inch, height=4*inch))
                    story.append(Spacer(1, 20))
            
            # Add recommendations
            if 'recommendations' in analysis_results:
                story.append(Paragraph("Recommendations", self.styles['CustomHeading']))
                for rec in analysis_results['recommendations']:
                    story.append(Paragraph(f"• {rec}", self.styles['CustomBody']))
                story.append(Spacer(1, 20))
            
            # Build the PDF
            doc.build(story)
            
            # Clean up plot files
            for path in plot_paths.values():
                try:
                    os.remove(path)
                except Exception as e:
                    self.logger.warning(f"Could not remove plot file {path}: {str(e)}")
            
            return report_filename
            
        except Exception as e:
            self.logger.error(f"Error in generate_report: {str(e)}")
            raise e
