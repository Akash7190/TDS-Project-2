# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "requests",
#   "ipykernel",
#   "python-dotenv",
# ]
# ///

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import json
from dotenv import load_dotenv
load_dotenv()


def analyze_data(df):
    # Just like a Pokédex entry, this summary condenses raw data into easily digestible insights.
    summary_stats = df.describe()

    # Treating missing values like Team Rocket—always blasting them off for cleaner datasets.
    missing_values = df.isnull().sum()
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr() if not numeric_df.empty else pd.DataFrame()
    return summary_stats, missing_values, corr_matrix

# Using IQR as our Hyper Beam to blast away outliers from this dataset.
def detect_outliers(df):
    df_numeric = df.select_dtypes(include=[np.number])

    Q1 = df_numeric.quantile(0.25)
    Q3 = df_numeric.quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df_numeric < (Q1 - 1.5 * IQR)) | (df_numeric > (Q3 + 1.5 * IQR))).sum()
    return outliers


# This function evolves the raw data, much like a Magikarp transforming into a Gyarados of insights
def visualize_data(corr_matrix, outliers, df, output_dir):
    plt.figure(figsize=(10, 8))

    # Heatmaps are the Charizard of visualizations—fiery and illuminating patterns in the data.
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Matrix')
    heatmap_file = os.path.join(output_dir, 'correlation_matrix.png')
    plt.savefig(heatmap_file)
    plt.close()

    if not outliers.empty and outliers.sum() > 0:
        plt.figure(figsize=(10, 6))
        outliers.plot(kind='bar', color='red')
        plt.title('Outliers Detection')
        plt.xlabel('Columns')
        plt.ylabel('Number of Outliers')
        outliers_file = os.path.join(output_dir, 'outliers.png')
        plt.savefig(outliers_file)
        plt.close()
    else:
        print("No outliers detected to visualize.")
        outliers_file = None 

    # Visualizations here are crafted to hit critical super-effective strikes on data comprehension.
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        selected_columns = [x for x in numeric_columns if "id" not in x.lower()] 
        selected_columns = [x for x in selected_columns if "isbn" not in x.lower()]   
        plt.figure(figsize=(10, 6))
        sns.histplot(df[selected_columns], kde=True, color='blue', bins=30)
        plt.title(f'Distribution')
        dist_plot_file = os.path.join(output_dir, f'distribution_.png')
        plt.savefig(dist_plot_file)
        plt.close()
    else:
        dist_plot_file = None
    return heatmap_file, outliers_file, dist_plot_file

# This README report serves as the ultimate Master Ball, capturing the essence of our analysis in one place.
def create_readme(summary_stats, missing_values, corr_matrix, outliers, output_dir):
    readme_file = os.path.join(output_dir, 'README.md')
    try:
        with open(readme_file, 'w') as f:
            f.write("# Automated Data Analysis Report\n\n")

            # Introduction Section
            f.write("## Introduction\n")
            f.write("This is an automated analysis of the dataset, providing summary statistics, visualizations, and insights from the data.\n\n")

            # Summary Statistics Section
            f.write("## Summary Statistics\n")
            f.write("The summary statistics of the dataset are as follows:\n\n")

            summary_table_header = "| Statistic | Column | Value |\n|-----------|--------|-------|\n"
            f.write(summary_table_header)

            # Populate table with summary statistics
            for column in summary_stats.columns:
                f.write(f"| Mean       | {column} | {summary_stats.loc['mean', column]:.2f} |\n")
                f.write(f"| Std Dev    | {column} | {summary_stats.loc['std', column]:.2f} |\n")
                f.write(f"| Min        | {column} | {summary_stats.loc['min', column]:.2f} |\n")
                f.write(f"| 25%        | {column} | {summary_stats.loc['25%', column]:.2f} |\n")
                f.write(f"| Median     | {column} | {summary_stats.loc['50%', column]:.2f} |\n")
                f.write(f"| 75%        | {column} | {summary_stats.loc['75%', column]:.2f} |\n")
                f.write(f"| Max        | {column} | {summary_stats.loc['max', column]:.2f} |\n")
            f.write("\n")

            # Missing Values Section
            f.write("## Missing Values\n")
            f.write("The following table shows the columns with missing values and their respective counts:\n\n")

            missing_table_header = "| Column | Missing Values Count |\n|--------|----------------------|\n"
            f.write(missing_table_header)

            for column, count in missing_values.items():
                f.write(f"| {column} | {count} |\n")
            f.write("\n")

            # Outliers Detection Section
            f.write("## Outliers Detection\n")
            f.write("The table below summarizes the outliers detected using the IQR method:\n\n")

            outliers_table_header = "| Column | Outlier Count |\n|--------|---------------|\n"
            f.write(outliers_table_header)

            for column, count in outliers.items():
                f.write(f"| {column} | {count} |\n")
            f.write("\n")

            # Correlation Matrix Section
            f.write("## Correlation Matrix\n")
            f.write("The correlation matrix below highlights the relationships between numerical features:\n\n")
            f.write("![Correlation Matrix](correlation_matrix.png)\n\n")

            # Outliers Visualization Section
            f.write("## Outliers Visualization\n")
            f.write("The chart below visualizes the number of outliers detected in each column:\n\n")
            f.write("![Outliers](outliers.png)\n\n")

            # Distribution Plot Section
            f.write("## Distribution of Data\n")
            f.write("The following plot shows the distribution of the first numerical column in the dataset:\n\n")
            f.write("![Distribution](distribution_.png)\n\n")

            # Conclusion Section
            f.write("## Conclusion\n")
            f.write("This analysis provides a detailed overview of the dataset, including summary statistics, missing values, outlier detection, and correlation analysis.\n")
            f.write("The generated visualizations and statistical insights offer valuable understanding of the data's patterns and relationships.\n\n")

            # Data Story Section
            f.write("## Data Story\n")
            f.write("This section can be customized to narrate key insights and findings derived from the data.\n")

        return readme_file
    except Exception as e:
        print(f"Error writing to README.md: {e}")
        return None

def question_llm(prompt, context):
    try:
        token = os.getenv("AIPROXY_TOKEN")
        api_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

        # Construct a detailed and engaging prompt for the AI
        full_prompt = f"""
        Using the provided context and data analysis prompt, craft a compelling and cohesive story. The story should:
        
        1. Begin with an engaging introduction that sets the stage for the analysis.
        2. Feature a well-developed body that delves into the data, explaining its significance and exploring key insights.
        3. Conclude with a thoughtful summary that ties everything together and highlights potential implications or lessons.
        
        Ensure the story is:
        - Divided into clear paragraphs for readability.
        - Richly detailed and creative, making the data come to life.
        - Smoothly transitioned, maintaining a logical flow throughout.
        
        Context:
        {context}

        Data Analysis Prompt:
        {prompt}
        
        Please provide a narrative that captivates and informs the reader.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            story = response.json()['choices'][0]['message']['content'].strip()
            return story
        else:
            print(f"Error with request: {response.status_code} - {response.text}")
            return "Failed to generate story."

    except Exception as e:
        print(f"Error: {e}")
        return "Failed to generate story."


def main(csv_file):
    try:
        df = pd.read_csv(csv_file, encoding='ISO-8859-1')
    except UnicodeDecodeError as e:
        print(f"Error reading file: {e}")
        return
    stats_summary, missing_values_summary, correlation = analyze_data(df)
    outliers = detect_outliers(df)

    output_dir = "."
    os.makedirs(output_dir, exist_ok=True)
    heatmap_file, outliers_file, dist_plot_file = visualize_data(correlation, outliers, df, output_dir)
    story = question_llm("Generate a nice and creative story from the analysis", 
                         context=f"Dataset Analysis:\nSummary Statistics:\n{stats_summary}\n\nMissing Values:\n{missing_values_summary}\n\nCorrelation Matrix:\n{correlation}\n\nOutliers:\n{outliers}")

    readme_file = create_readme(stats_summary, missing_values_summary, correlation, outliers, output_dir)
    if readme_file:
        try:
            with open(readme_file, 'a') as f:
                f.write("## Story\n")
                f.write(f"{story}\n")
        except Exception as e:
            print(f"Error appending story to README.md: {e}")
    else:
        print("Error generating the README.md file.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: uv run autolysis.py <dataset_path>")
        sys.exit(1)
    main(sys.argv[1])
