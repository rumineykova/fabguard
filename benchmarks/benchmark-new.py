import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def extract_results(file_path, exclude_folder='netherlands'):
    with open(file_path, 'r') as file:
        data = file.read()

    pattern = re.compile(
        r"Folder: (.*?)\nElapsed Time: ([\d.]+) seconds\nLine Counts:\n  locations.csv: (\d+)\n  routes.csv: (\d+)\n  closures.csv: (\d+)\nTotal Lines: (\d+)"
    )
    matches = pattern.findall(data)

    results = []
    for match in matches:
        folder, elapsed_time, locations, routes, closures, total_lines = match
        if folder not in exclude_folder:
            results.append({
                'Folder': folder,
                'Elapsed Time': float(elapsed_time),
                'locations.csv': int(locations),
                'routes.csv': int(routes),
                'closures.csv': int(closures),
                'Total Lines': int(total_lines)
            })
        else:
            print(folder)

    return pd.DataFrame(results)

def combine_results(file_paths):
    combined_df = pd.DataFrame()
    for file_path in file_paths:
        df = extract_results(file_path)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

# List of results files from all runs
results_files = ['results/results_run1.txt', 'results/results_run2.txt', 'results/results_run3.txt', 'results/results_run4.txt', 'results/results_run5.txt']

# Combine results from all files
results_df = combine_results(results_files)
results_df = results_df.apply(pd.to_numeric, errors='coerce')

# Compute average and standard deviation for total lines
total_lines_mean = results_df['Total Lines'].mean()
total_lines_std = results_df['Total Lines'].std()

# Summary Statistics
print(f"Average Total Lines: {total_lines_mean}")
print(f"Total Lines Standard Deviation: {total_lines_std}")

# Bar Chart for Total Lines with Average and Deviations
plt.figure(figsize=(14, 8))
sns.barplot(x='Folder', y='Total Lines', data=results_df)
plt.axhline(y=total_lines_mean, color='r', linestyle='--', label='Average')
plt.axhline(y=total_lines_mean + total_lines_std, color='g', linestyle='--', label='+1 Std Dev')
plt.axhline(y=total_lines_mean - total_lines_std, color='g', linestyle='--', label='-1 Std Dev')
plt.title('Total Lines for Each Folder with Average and Deviations')
plt.xlabel('Folder')
plt.ylabel('Total Lines')
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.savefig('figures/total_lines_barchart.png')
plt.show()

# Histogram of Elapsed Time
plt.figure(figsize=(10, 6))
sns.histplot(results_df['Elapsed Time'], kde=True)
plt.title('Histogram of Elapsed Times')
plt.xlabel('Elapsed Time (seconds)')
plt.ylabel('Frequency')
plt.savefig('figures/elapsed_time_histogram.png')
plt.show()

# Scatter Plot of Total Lines vs. Elapsed Time
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Total Lines', y='Elapsed Time', data=results_df)
plt.title('Total Lines vs. Elapsed Time')
plt.xlabel('Total Lines')
plt.ylabel('Elapsed Time (seconds)')
plt.savefig('figures/total_lines_vs_elapsed_time.png')
plt.show()

# Box Plot for Elapsed Time
plt.figure(figsize=(10, 6))
sns.boxplot(y=results_df['Elapsed Time'])
plt.title('Box Plot of Elapsed Time')
plt.ylabel('Elapsed Time (seconds)')
plt.savefig('figures/elapsed_time_boxplot.png')
plt.show()

# Line Plot for Cumulative Lines Processed vs. Cumulative Time
results_df = results_df.sort_values(by='Total Lines').reset_index(drop=True)
results_df['Cumulative Lines'] = results_df['Total Lines'].cumsum()
results_df['Cumulative Time'] = results_df['Elapsed Time'].cumsum()

plt.figure(figsize=(14, 8))
plt.plot(results_df['Cumulative Lines'], results_df['Cumulative Time'], marker='o')
plt.title('Cumulative Lines Processed vs. Cumulative Time')
plt.xlabel('Cumulative Lines Processed')
plt.ylabel('Cumulative Time (seconds)')
plt.grid(True)
plt.savefig('figures/cumulative_lines_vs_cumulative_time.png')
plt.show()

# Heatmap of Correlations
plt.figure(figsize=(10, 6))
sns.heatmap(results_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Heatmap of Correlations')
plt.savefig('figures/correlation_heatmap.png')
plt.show()
