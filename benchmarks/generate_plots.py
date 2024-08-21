import numpy as np
import matplotlib.pyplot as plt
import seaborn

# Set a common style for all plots
plt.style.use('ggplot')

# Create a figure with 4 subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))

# 1. Median Execution Time vs Columns Per File
columns = np.array([20, 40, 60, 80, 100])
exec_time_columns = np.array([4.43, 4.45, 4.46, 4.45, 4.45])

ax1.errorbar(columns, exec_time_columns, yerr=0.02, fmt='o-', capsize=5)
ax1.set_xlabel('Columns Per File')
ax1.set_ylabel('Median Execution Time (s)')
ax1.set_title('Median Execution Time vs Columns Per File')
ax1.set_ylim(4.40, 4.50)

# Add trend line
z = np.polyfit(columns, exec_time_columns, 1)
p = np.poly1d(z)
ax1.plot(columns, p(columns), "r--", alpha=0.8)

# 2. Median Execution Time vs Data Complexity
complexity = np.array([2, 4, 6, 8, 10])
exec_time_complexity = np.array([4.46, 4.48, 4.47, 4.46, 4.45])

ax2.errorbar(complexity, exec_time_complexity, yerr=0.02, fmt='o-', capsize=5)
ax2.set_xlabel('Data Complexity')
ax2.set_ylabel('Median Execution Time (s)')
ax2.set_title('Median Execution Time vs Data Complexity')
ax2.set_ylim(4.40, 4.50)

# Add trend line
z = np.polyfit(complexity, exec_time_complexity, 1)
p = np.poly1d(z)
ax2.plot(complexity, p(complexity), "r--", alpha=0.8)

# 3. Median Execution Time vs Num Files
num_files = np.array([0, 20, 40, 60, 80, 100])
exec_time_files = np.array([0, 20, 40, 60, 80, 100])

ax3.plot(num_files, exec_time_files, 'o-')
ax3.set_xlabel('Number of Files')
ax3.set_ylabel('Median Execution Time (s)')
ax3.set_title('Median Execution Time vs Number of Files')

# 4. Median Execution Time vs Rows Per File
rows = np.array([200, 400, 600, 800, 1000])
exec_time_rows = np.array([4.48, 4.42, 4.52, 4.46, 4.44])

ax4.bar(rows, exec_time_rows, width=100, alpha=0.7)
ax4.set_xlabel('Rows Per File')
ax4.set_ylabel('Median Execution Time (s)')
ax4.set_title('Median Execution Time vs Rows Per File')
ax4.set_ylim(4.35, 4.55)

# Add trend line
z = np.polyfit(rows, exec_time_rows, 1)
p = np.poly1d(z)
ax4.plot(rows, p(rows), "r--", alpha=0.8)

# Adjust layout and display
plt.tight_layout()
plt.savefig('figures1/fabguard_performance_graphs.png', dpi=300, bbox_inches='tight')
plt.show()