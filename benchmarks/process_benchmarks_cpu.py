import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_json_results(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def combine_results(file_paths, exclude_folder='netherlands'):
    combined_df = pd.DataFrame()
    for file_path in file_paths:
        data = load_json_results(file_path)

        filtered_data = [item for item in data if item['folder'] != exclude_folder]
        df = pd.json_normalize(filtered_data)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

# List of results files from all runs
results_files = ['results/results_run1.json', 'results/results_run2.json', 'results/results_run3.json']

# Combine results from all files
results_df = combine_results(results_files)

# Convert relevant columns to numeric
numeric_columns = ['elapsed_time', 'total_lines', 'resource_usage.cpu_usage', 'resource_usage.memory_usage', 'resource_usage.peak_memory']
results_df[numeric_columns] = results_df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Summary Statistics
print("Summary Statistics:")
print(results_df[numeric_columns].describe())

# Success Rate
success_rate = (results_df['status'] == 'Passed').mean() * 100
print(f"\nSuccess Rate: {success_rate:.2f}%")

# Bar Chart for Total Lines with Average and Deviations
plt.figure(figsize=(14, 8))
sns.barplot(x='folder', y='total_lines', data=results_df)
plt.axhline(y=results_df['total_lines'].mean(), color='r', linestyle='--', label='Average')
plt.axhline(y=results_df['total_lines'].mean() + results_df['total_lines'].std(), color='g', linestyle='--', label='+1 Std Dev')
plt.axhline(y=results_df['total_lines'].mean() - results_df['total_lines'].std(), color='g', linestyle='--', label='-1 Std Dev')
plt.title('Total Lines for Each Folder with Average and Deviations')
plt.xlabel('Folder')
plt.ylabel('Total Lines')
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.savefig('figures/total_lines_barchart.png')
plt.close()

# Histogram of Elapsed Time
plt.figure(figsize=(10, 6))
sns.histplot(results_df['elapsed_time'], kde=True)
plt.title('Histogram of Elapsed Times')
plt.xlabel('Elapsed Time (seconds)')
plt.ylabel('Frequency')
plt.savefig('figures/elapsed_time_histogram.png')
plt.close()

# Scatter Plot of Total Lines vs. Elapsed Time
plt.figure(figsize=(10, 6))
sns.scatterplot(x='total_lines', y='elapsed_time', data=results_df)
plt.title('Total Lines vs. Elapsed Time')
plt.xlabel('Total Lines')
plt.ylabel('Elapsed Time (seconds)')
plt.savefig('figures/total_lines_vs_elapsed_time.png')
plt.close()

# Box Plot for Elapsed Time
plt.figure(figsize=(10, 6))
sns.boxplot(y=results_df['elapsed_time'])
plt.title('Box Plot of Elapsed Time')
plt.ylabel('Elapsed Time (seconds)')
plt.savefig('figures/elapsed_time_boxplot.png')
plt.close()

# Line Plot for Cumulative Lines Processed vs. Cumulative Time
results_df = results_df.sort_values(by='total_lines').reset_index(drop=True)
results_df['Cumulative Lines'] = results_df['total_lines'].cumsum()
results_df['Cumulative Time'] = results_df['elapsed_time'].cumsum()

plt.figure(figsize=(14, 8))
plt.plot(results_df['Cumulative Lines'], results_df['Cumulative Time'], marker='o')
plt.title('Cumulative Lines Processed vs. Cumulative Time')
plt.xlabel('Cumulative Lines Processed')
plt.ylabel('Cumulative Time (seconds)')
plt.grid(True)
plt.savefig('figures/cumulative_lines_vs_cumulative_time.png')
plt.close()

# Heatmap of Correlations
plt.figure(figsize=(12, 8))
correlation_columns = numeric_columns + ['Cumulative Lines', 'Cumulative Time']
sns.heatmap(results_df[correlation_columns].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Heatmap of Correlations')
plt.savefig('figures/correlation_heatmap.png')
plt.close()

# New plots for CPU and Memory usage
plt.figure(figsize=(10, 6))
sns.scatterplot(x='total_lines', y='resource_usage.cpu_usage', data=results_df)
plt.title('Total Lines vs. CPU Usage')
plt.xlabel('Total Lines')
plt.ylabel('CPU Usage (%)')
plt.savefig('figures/total_lines_vs_cpu_usage.png')
plt.close()

plt.figure(figsize=(10, 6))
sns.scatterplot(x='total_lines', y='resource_usage.memory_usage', data=results_df)
plt.title('Total Lines vs. Memory Usage')
plt.xlabel('Total Lines')
plt.ylabel('Memory Usage (%)')
plt.savefig('figures/total_lines_vs_memory_usage.png')
plt.close()

plt.figure(figsize=(10, 6))
sns.scatterplot(x='resource_usage.cpu_usage', y='resource_usage.memory_usage', data=results_df)
plt.title('CPU Usage vs. Memory Usage')
plt.xlabel('CPU Usage (%)')
plt.ylabel('Memory Usage (%)')
plt.savefig('figures/cpu_usage_vs_memory_usage.png')
plt.close()

print("All plots have been saved in the 'figures' directory.")