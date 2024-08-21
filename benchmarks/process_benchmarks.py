import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Function to extract information from the results file
def extract_results(file_path):
    with open(file_path, 'r') as file:
        data = file.read()

    pattern = re.compile(r"Folder: (.*?)\nElapsed Time: ([\d.]+) seconds\nLine Counts:\n  locations.csv: (\d+)\n  routes.csv: (\d+)\n  closures.csv: (\d+)\nTotal Lines: (\d+)")
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

# Displaying the extracted results
print(results_df)

# Computing summary statistics
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

# Plotting the correlation
plt.scatter(results_df['Total Lines'], results_df['Elapsed Time'])
plt.xlabel('Total Lines')
plt.ylabel('Elapsed Time (seconds)')
plt.title('Correlation between Total Lines and Elapsed Time')
plt.show()

# Saving summary statistics to a file
with open('summary_statistics.txt', 'w') as file:
    for key, value in summary_stats.items():
        file.write(f"{key}: {value}\n")
