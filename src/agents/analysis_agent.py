import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class AnalysisAgent:
    def analyze(self, data):
        try:
            summary = self._generate_summary(data)
            trends = self._analyze_trends(data)
            return summary, trends
        except Exception as e:
            raise Exception(f"Error in analysis: {str(e)}")

    def _generate_summary(self, data):
        summary = []
        
        # Basic dataset information
        summary.append(f"Dataset Overview:")
        summary.append(f"- Total Records: {len(data)}")
        summary.append(f"- Total Features: {len(data.columns)}")
        summary.append(f"- Columns: {', '.join(data.columns)}")
        
        # Analyze each column
        for column in data.columns:
            col_type = data[column].dtype
            summary.append(f"\n{column} Analysis:")
            
            if pd.api.types.is_numeric_dtype(data[column]):
                # Numeric column analysis
                stats = data[column].describe()
                summary.append(f"- Type: Numeric")
                summary.append(f"- Mean: {stats['mean']:.2f}")
                summary.append(f"- Median: {data[column].median():.2f}")
                summary.append(f"- Min: {stats['min']:.2f}")
                summary.append(f"- Max: {stats['max']:.2f}")
                summary.append(f"- Missing Values: {data[column].isnull().sum()}")
            
            elif pd.api.types.is_datetime64_any_dtype(data[column]):
                # Date column analysis
                summary.append(f"- Type: Date/Time")
                summary.append(f"- Earliest: {data[column].min()}")
                summary.append(f"- Latest: {data[column].max()}")
                summary.append(f"- Missing Values: {data[column].isnull().sum()}")
            
            else:
                # Categorical column analysis
                summary.append(f"- Type: Categorical")
                summary.append(f"- Unique Values: {data[column].nunique()}")
                summary.append(f"- Top Categories: {', '.join(data[column].value_counts().nlargest(5).index.astype(str))}")
                summary.append(f"- Missing Values: {data[column].isnull().sum()}")
        
        return "\n".join(summary)

    def _analyze_trends(self, data):
        trends = []
        
        # Analyze numeric columns for trends
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            trends.append("Numeric Trends:")
            for col in numeric_cols:
                trends.append(f"\n{col}:")
                trends.append(f"- Overall Trend: {'Increasing' if data[col].corr(pd.Series(range(len(data)))) > 0 else 'Decreasing'}")
                trends.append(f"- Volatility: {'High' if data[col].std() > data[col].mean() else 'Low'}")
        
        # Analyze categorical columns for distribution changes
        categorical_cols = data.select_dtypes(exclude=[np.number]).columns
        if len(categorical_cols) > 0:
            trends.append("\nCategorical Distributions:")
            for col in categorical_cols:
                if data[col].nunique() < 10:  # Only analyze if not too many unique values
                    distribution = data[col].value_counts(normalize=True)
                    trends.append(f"\n{col}:")
                    for cat, pct in distribution.nlargest(3).items():
                        trends.append(f"- {cat}: {pct:.1%}")
        
        # Correlation analysis for numeric columns
        if len(numeric_cols) > 1:
            trends.append("\nStrong Correlations:")
            corr_matrix = data[numeric_cols].corr()
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr = corr_matrix.iloc[i, j]
                    if abs(corr) > 0.5:  # Only show strong correlations
                        trends.append(f"- {numeric_cols[i]} vs {numeric_cols[j]}: {corr:.2f}")
        
        return "\n".join(trends)
