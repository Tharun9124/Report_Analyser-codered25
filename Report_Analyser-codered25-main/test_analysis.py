import pandas as pd
from src.agents.medical_llm_agent import MedicalLLMAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.report_generation_agent import ReportGenerationAgent

def main():
    # Load the sample healthcare data
    df = pd.read_csv('data/raw/sample_healthcare_data.csv')
    print("Data loaded successfully. Shape:", df.shape)

    # Initialize agents
    medical_agent = MedicalLLMAgent()
    viz_agent = VisualizationAgent()
    report_agent = ReportGenerationAgent()

    # Generate medical insights
    print("\nGenerating medical insights...")
    insights = medical_agent.analyze_health_data(df)
    
    print("\nKey Medical Insights:")
    for insight in insights.get('insights', []):
        print(f"- {insight}")
    
    print("\nRisk Factors:")
    for risk in insights.get('risk_factors', []):
        print(f"- {risk}")
    
    print("\nRecommendations:")
    for rec in insights.get('recommendations', []):
        print(f"- {rec}")

    # Generate visualizations
    print("\nGenerating visualizations...")
    viz_data = viz_agent.generate_preview_data(df)
    print("Visualization data generated")

    # Generate report
    print("\nGenerating comprehensive report...")
    report_path, report_insights = report_agent.generate_report(
        df,
        analysis_depth='detailed',
        visual_style='modern'
    )
    print(f"\nReport generated successfully at: {report_path}")

if __name__ == "__main__":
    main()
