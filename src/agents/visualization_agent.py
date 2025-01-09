import seaborn as sns
import matplotlib.pyplot as plt

class VisualizationAgent:
    def generate(self, data):
        print("Generating visualizations...")
        visualizations = {}

        # Convert non-numeric columns to numeric or drop them
        numeric_data = data.select_dtypes(include=["number"])  # Select only numeric columns

        if numeric_data.empty:
            raise ValueError("The dataset does not contain any numeric columns for visualization.")

        # Correlation Heatmap
        try:
            plt.figure(figsize=(10, 8))
            heatmap = sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm")
            heatmap_path = "./output/heatmap.png"
            plt.title("Correlation Heatmap")
            plt.savefig(heatmap_path)
            plt.close()
            visualizations["heatmap"] = heatmap_path
            print(f"Correlation heatmap saved at {heatmap_path}")
        except Exception as e:
            print(f"Error generating heatmap: {e}")

        return visualizations
