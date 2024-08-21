import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Function to extract information from the results.txt file
def extract_results(file_path):
    with open(file_path, 'r') as file:
        data = file.read()

    pattern = re.compile(
        r"Folder: (.*?)\nElapsed Time: ([\d.]+) seconds\nLine Counts:\n  locations.csv: (\d+)\n  routes.csv: (\d+)\n  closures.csv: (\d+)\nTotal Lines: (\d+)"
    )
    matches = pattern.findall(data)

    results = []
    for match in matches:
        folder, elapsed_time, locations, routes, closures, total_lines = match
        results.append({
            'Folder': folder,
            'Elapsed Time': float(elapsed_time),
            'locations.csv': int(locations),
            'routes.csv': int(routes),
            'closures.csv': int(closures),
            'Total Lines': int(total_lines)
        })

    return pd.DataFrame(results)

# Extracting results from the file
results_df = extract_results('/Users/rumyananeykova/Dev/FabSim3/results.txt')

# Compute summary statistics
total_time = results_df['Elapsed Time'].sum()
mean_time = results_df['Elapsed Time'].mean()
median_time = results_df['Elapsed Time'].median()
correlation = results_df[['Total Lines', 'Elapsed Time']].corr().iloc[0, 1]

summary_stats = {
    'Total Time': total_time,
    'Mean Time': mean_time,
    'Median Time': median_time,
    'Correlation (Total Lines vs Elapsed Time)': correlation
}

print("\nSummary Statistics:")
for key, value in summary_stats.items():
    print(f"{key}: {value}")

# Box Plot for Elapsed Time
plt.figure(figsize=(10, 6))
sns.boxplot(y=results_df['Elapsed Time'])
plt.title('Distribution of Elapsed Time')
plt.ylabel('Elapsed Time (seconds)')
plt.savefig('box_plot_elapsed_time.png')
plt.show()

# Bar Chart for Total Lines vs Elapsed Time
plt.figure(figsize=(14, 8))
sns.barplot(x='Total Lines', y='Elapsed Time', data=results_df)
plt.title('Total Lines vs Elapsed Time')
plt.xlabel('Total Lines')
plt.ylabel('Elapsed Time (seconds)')
plt.savefig('bar_chart_total_lines_vs_elapsed_time.png')
plt.show()

# Histogram of Elapsed Times
plt.figure(figsize=(10, 6))
sns.histplot(results_df['Elapsed Time'], kde=True)
plt.title('Histogram of Elapsed Times')
plt.xlabel('Elapsed Time (seconds)')
plt.ylabel('Frequency')
plt.savefig('histogram_elapsed_times.png')
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
plt.savefig('line_plot_cumulative_lines_vs_cumulative_time.png')
plt.show()

# Heatmap of Correlations
plt.figure(figsize=(10, 6))
sns.heatmap(results_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Heatmap of Correlations')
plt.savefig('heatmap_correlations.png')
plt.show()

# Save summary statistics to a file
with open('summary_statistics.txt', 'w') as file:
    for key, value in summary_stats.items():
        file.write(f"{key}: {value}\n")
