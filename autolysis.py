import os
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from dotenv import load_dotenv

# File paths
load_dotenv()
data_path = "data.csv"  

# Proxy API details
API_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
API_TOKEN = os.getenv("AIPROXY_TOKEN")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def load_data(path):
    """Load data from CSV with proper encoding."""
    try:
        df = pd.read_csv(path, encoding='ISO-8859-1')
        print("Data loaded successfully.")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def send_to_llm(summary, description):
    """Send dataset summary and description to the LLM for analysis."""
    messages = [
        {"role": "user", "content": f"Here is the summary of a dataset:\n\n{summary}\n\nDescription:\n{description}\n\nPlease analyze it and provide insights."}
    ]
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            analysis = response.json().get('choices', [{}])[0].get('message', {}).get('content', "No content received.")
            print("Analysis received from LLM.")
            return analysis
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Failed to connect to LLM: {e}")
        return None

def generate_insights(df):
    """Generate simple, readable insights from the data."""
    insights = ""
    
    # Basic descriptive statistics
    insights += "### Key Statistics\n\n"
    insights += f"Total rows: {df.shape[0]}, Total columns: {df.shape[1]}\n"
    insights += "\n### Descriptive Statistics:\n"
    insights += df.describe(include='all').to_string() + "\n"
    
    # Correlations (only for numeric columns)
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        correlations = numeric_df.corr()
        insights += "\n### Correlation Analysis:\n"
        insights += correlations.to_string() + "\n"
    else:
        insights += "\n### Correlation Analysis:\nNo numeric columns available for correlation.\n"
    
    # Missing values
    missing_values = df.isnull().sum()
    insights += "\n### Missing Values:\n"
    insights += missing_values[missing_values > 0].to_string() + "\n"
    
    return insights

def generate_visualizations(df):
    """Create up to 3 visualizations for the dataset and generate summaries."""
    graph_summaries = {}

    try:
        numeric_columns = df.select_dtypes(include=['number']).columns
        selected_columns = [x for x in numeric_columns if "id" not in x.lower()] 
        selected_columns = [x for x in selected_columns if "isbn" not in x.lower()] 
        selected_columns = selected_columns[:4]

        for column in selected_columns:
            plt.figure(figsize=(6, 6))  # Ensure images are under 512x512 pixels
            sns.histplot(df[column], kde=True, color='blue')
            plt.title(f'Distribution of {column}')
            
            graph_filename = f'{column}_distribution.png'
            plt.savefig(graph_filename, dpi=100)  # Save in the current directory
            
            plt.close()

            # Summarize the graph
            graph_summaries[column] = {
                'filename_home': graph_filename,  # Image saved in the current working directory
                'summary': f"The graph above shows the distribution of the '{column}' column. "
                           f"It visualizes the frequency distribution of the values. "
                           f"Look for the central tendency, spread, and any possible skewness in the distribution. "
                           f"From the descriptive statistics, the mean of this column is {df[column].mean():.2f}, "
                           f"and the standard deviation is {df[column].std():.2f}."
            }

        print("Graphs saved in the current directory.")
        return graph_summaries
    except Exception as e:
        print(f"Error generating graphs: {e}")
        return None



def send_analysis_for_description(analysis):
    """Send the analysis text to the LLM to get a detailed description."""
    messages = [
        {"role": "user", "content": f"Here is the analysis of the dataset:\n\n{analysis}\n\nPlease provide a detailed description of this analysis in simple terms."}
    ]
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            description = response.json().get('choices', [{}])[0].get('message', {}).get('content', "No description received.")
            print("Description of analysis received from LLM.")
            return description
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Failed to connect to LLM: {e}")
        return None

def compile_markdown_report(df, insights, description, graph_summaries, filename):
    """Generate Markdown report summarizing the analysis."""
    filename = "README.md"
    try:
        with open(filename, 'w') as md_file:
            md_file.write(f"# Dataset Analysis Report: {filename}\n\n")
            md_file.write(f"## Dataset Summary\n\n")
            md_file.write(f"**Shape:** {df.shape}\n\n")
            md_file.write(f"**Columns:**\n\n")
            md_file.write(", ".join(df.columns) + "\n\n")
            
            md_file.write(f"## Insights and Analysis\n\n{insights}\n\n")
            
            if description:
                md_file.write(f"## Description of Analysis\n\n{description}\n\n")

            if graph_summaries:
                md_file.write(f"## Visualizations and Descriptions\n\n")
                for column, summary in graph_summaries.items():
                    md_file.write(f"### {column} Distribution\n")
                    md_file.write(f"![{column}_distribution]({summary['filename_home']})\n\n")
                    md_file.write(f"{summary['summary']}\n\n")
        
        print(f"Markdown report generated: {filename}")
        return filename
    except Exception as e:
        print(f"Error generating Markdown file: {e}")
        return None


def main():
    print("Autolysis started.")

    # Load data
    if len(sys.argv) < 2:
        print("Usage: python autolysis.py <dataset.csv>")
        exit()

    data_path = sys.argv[1]
    df = load_data(data_path)

    if df is not None:
        # Generate insights
        insights = generate_insights(df)
        print("Insights generated from data.")

        # Send analysis to LLM for description in layman's terms
        description = send_analysis_for_description(insights)
        if description:
            # Generate visualizations
            graph_summaries = generate_visualizations(df)

            # Compile Markdown Report
            markdown_filename = os.path.splitext(os.path.basename(data_path))[0] + ".md"
            compile_markdown_report(df, insights, description, graph_summaries, markdown_filename)
        else:
            print("Failed to get description from LLM.")
    else:
        print("Failed to load dataset.")

if __name__ == "__main__":
    main()