import os
import time

import psutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
from faker import Faker

fake = Faker()

def generate_synthetic_locations(num_rows, num_columns, data_complexity, error_rate):
    data = {
        'name': [fake.city() for _ in range(num_rows)],
        'region': [fake.state() for _ in range(num_rows)],
        'country': ['Ethiopia' for _ in range(num_rows)],
        'latitude': [fake.latitude() for _ in range(num_rows)],
        'longitude': [fake.longitude() for _ in range(num_rows)],
        'location_type': np.random.choice(['conflict_zone', 'town', 'camp', 'forwarding_hub', 'marker', 'idpcamp'],
                                          num_rows),
        'conflict_date': [np.random.randint(0, 101) if np.random.random() < 0.7 else None for _ in range(num_rows)],
        'population': [np.random.randint(1000, 1000001) for _ in range(num_rows)]
    }

    # Add extra columns based on data_complexity
    data_types = ['str', 'int', 'float', 'date', 'bool', 'category']
    for i in range(8, num_columns):
        dtype = np.random.choice(data_types[:data_complexity])
        if dtype == 'str':
            data[f'extra_col_{i}'] = [fake.word() if np.random.random() > error_rate else '' for _ in range(num_rows)]
        elif dtype == 'int':
            data[f'extra_col_{i}'] = [np.random.randint(0, 1001) if np.random.random() > error_rate else np.nan for _ in
                                      range(num_rows)]
        elif dtype == 'float':
            data[f'extra_col_{i}'] = [np.random.uniform(0, 1) if np.random.random() > error_rate else np.nan for _ in
                                      range(num_rows)]
        elif dtype == 'date':
            data[f'extra_col_{i}'] = [fake.date_object() if np.random.random() > error_rate else None for _ in
                                      range(num_rows)]
        elif dtype == 'bool':
            data[f'extra_col_{i}'] = [np.random.choice([True, False]) if np.random.random() > error_rate else None for _
                                      in range(num_rows)]
        elif dtype == 'category':
            categories = [fake.word() for _ in range(5)]
            data[f'extra_col_{i}'] = [np.random.choice(categories) if np.random.random() > error_rate else np.nan for _
                                      in range(num_rows)]

    df = pd.DataFrame(data)

    # Introduce errors based on error_rate
    num_errors = int(num_rows * error_rate)
    for _ in range(num_errors):
        row = np.random.randint(0, num_rows)
        col = np.random.choice(list(data.keys()))
        if col == 'name':
            df.at[row, col] = ''
        elif col in ['latitude', 'longitude']:
            df.at[row, col] = np.random.uniform(-1000, 1000)
        elif col == 'location_type':
            df.at[row, col] = 'invalid_type'
        elif col == 'conflict_date':
            df.at[row, col] = -1
        elif col == 'population':
            df.at[row, col] = -1000

    return df

def generate_multiple_files(num_files, rows_per_file, columns_per_file, base_path, data_complexity, error_rate):
    for i in range(num_files):
        df = generate_synthetic_locations(rows_per_file, columns_per_file, data_complexity, error_rate)
        folder_path = os.path.join(base_path, f"test_folder_{i + 1}/input_csv")
        os.makedirs(folder_path, exist_ok=True)
        df.to_csv(os.path.join(folder_path, 'locations.csv'), index=False)

        # Create empty files for other required inputs
        open(os.path.join(folder_path, 'routes.csv'), 'w').close()
        open(os.path.join(folder_path, 'closures.csv'), 'w').close()


def generate_pandera_schema(num_columns, data_complexity):
    schema = """
import pandera as pa
from pandera.typing import Series

class LocationsTestScheme(pa.DataFrameModel):
    name: Series[str] = pa.Field(nullable=False)
    region: Series[str] = pa.Field()
    country: Series[str] = pa.Field()
    latitude: Series[float] = pa.Field(ge=-90, le=90)
    longitude: Series[float] = pa.Field(ge=-180, le=180)
    location_type: Series[str] = pa.Field(isin=["conflict_zone", "town", "camp", "forwarding_hub", "marker", "idpcamp"])
    conflict_date: Series[float] = pa.Field(nullable=True, ge=0)
    population: Series[float] = pa.Field(ge=0, nullable=True)
    """

    data_types = ['str', 'int', 'float', 'date', 'bool', 'category']
    for i in range(8, num_columns):
        dtype = np.random.choice(data_types[:data_complexity])
        if dtype == 'str':
            schema += f"extra_col_{i}: Series[str] = pa.Field()\n"
        elif dtype == 'int':
            schema += f"extra_col_{i}: Series[int] = pa.Field(nullable=True)\n"
        elif dtype == 'float':
            schema += f"extra_col_{i}: Series[float] = pa.Field(nullable=True)\n"
        elif dtype == 'date':
            schema += f"extra_col_{i}: Series[pa.DateTime] = pa.Field(nullable=True)\n"
        elif dtype == 'bool':
            schema += f"extra_col_{i}: Series[bool] = pa.Field(nullable=True)\n"
        elif dtype == 'category':
            schema += f"extra_col_{i}: Series[str] = pa.Field(nullable=True)\n"

    return schema


def run_benchmark(base_path, base_path_test, num_files, rows_per_file, columns_per_file, data_complexity, error_rate):
    generate_multiple_files(num_files, rows_per_file, columns_per_file, base_path, data_complexity, error_rate)

    schema = generate_pandera_schema(columns_per_file, data_complexity)
    with open(os.path.join(base_path_test, 'locations_test_schema.py'), 'w') as f:
        f.write(schema)

    process = psutil.Process(os.getpid())

    # Measure initial memory
    initial_memory = process.memory_info().rss / 1024 / 1024  # Memory in MB

    start_time = time.time()

    peak_memory = initial_memory

    for i in range(num_files):
        folder_name = f"test_folder_{i + 1}"
        command = f"fabsim localhost flee_verify_input:{folder_name}"
        subprocess.run(command, shell=True, check=True)

        # Update peak memory after each file
        current_memory = process.memory_info().rss / 1024 / 1024
        peak_memory = max(peak_memory, current_memory)

    end_time = time.time()

    execution_time = end_time - start_time
    memory_used = peak_memory - initial_memory

    # Ensure memory usage is non-negative
    memory_used = max(0, memory_used)

    return execution_time, memory_used

def benchmark_dimension(dimension_name, dimension_values, base_path, base_path_test, num_runs=5, warmup_runs=2,
                        **fixed_params):
    all_execution_times = []
    all_memory_usages = []

    for value in dimension_values:
        print(f"Benchmarking {dimension_name}: {value}")
        params = fixed_params.copy()
        params[dimension_name] = value

        # Warm-up runs
        for _ in range(warmup_runs):
            run_benchmark(base_path, base_path_test, **params)

        # Actual benchmark runs
        execution_times = []
        memory_usages = []
        for _ in range(num_runs):
            time_taken, memory_used = run_benchmark(base_path, base_path_test, **params)
            execution_times.append(time_taken)
            memory_usages.append(memory_used)

        all_execution_times.append(execution_times)
        all_memory_usages.append(memory_usages)

    # Calculate median and standard deviation
    median_execution_times = [np.median(times) for times in all_execution_times]
    std_execution_times = [np.std(times) for times in all_execution_times]
    median_memory_usages = [np.median(usages) for usages in all_memory_usages]
    std_memory_usages = [np.std(usages) for usages in all_memory_usages]

    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

    ax1.errorbar(dimension_values, median_execution_times, yerr=std_execution_times, fmt='o-', capsize=5)
    ax1.set_xlabel(dimension_name.replace('_', ' ').title())
    ax1.set_ylabel('Median Execution Time (s)')
    ax1.set_title(f'Median Execution Time vs {dimension_name.replace("_", " ").title()}')

    ax2.errorbar(dimension_values, median_memory_usages, yerr=std_memory_usages, fmt='o-', color='r', capsize=5)
    ax2.set_xlabel(dimension_name.replace('_', ' ').title())
    ax2.set_ylabel('Median Memory Usage (MB)')
    ax2.set_title(f'Median Memory Usage vs {dimension_name.replace("_", " ").title()}')

    plt.tight_layout()
    plt.savefig(f'figures/benchmark_results_{dimension_name}.png')
    plt.close()

    # Print summary statistics
    print(f"\nSummary Statistics for {dimension_name}:")
    for i, value in enumerate(dimension_values):
        print(f"  {dimension_name} = {value}:")
        print(f"    Median Execution Time: {median_execution_times[i]:.2f} s (±{std_execution_times[i]:.2f})")
        print(f"    Median Memory Usage: {median_memory_usages[i]:.2f} MB (±{std_memory_usages[i]:.2f})")


if __name__ == "__main__":
    # base path for inputs
    base_path = "/Users/rumyananeykova/Dev/FabSim3/plugins/FabFlee/config_files/"
    # base path for tests
    base_path_test = "/Users/rumyananeykova/Dev/FabSim3/plugins/FabFlee/fab_guard/tests"
    #os.makedirs(base_path, exist_ok=True)

    # Benchmark number of files
    #generate_multiple_files(100, rows_per_file=100,
    #                        columns_per_file=10,base_path=base_path, data_complexity=3, error_rate=0.05)

    #schema = generate_pandera_schema(10, data_complexity = 3)
    #with open(os.path.join(base_path_test, 'locations_test_schema.py'), 'w') as f:
    #    f.write(schema)
    """
    benchmark_dimension('num_files', [1, 5,10, 20,30, 40, 50,60, 70, 80, 90, 100], base_path,base_path_test,
                        rows_per_file=100, columns_per_file=20, data_complexity=3, error_rate=0.05)

    # Benchmark number of rows per file

    benchmark_dimension('rows_per_file', [100,200, 300, 400, 500, 600, 700, 800, 900, 1000], base_path, base_path_test,
                        num_files=5, columns_per_file=20, data_complexity=3, error_rate=0.05)
    
    # Benchmark number of columns
    benchmark_dimension('columns_per_file', [10, 20,30, 40, 50, 60, 70, 80, 90, 100], base_path, base_path_test,
                        num_files=5, rows_per_file=1000, data_complexity=3, error_rate=0.05)

    """
    # Benchmark data complexity
    benchmark_dimension('data_complexity', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], base_path,base_path_test,
                        num_files=5, rows_per_file=100, columns_per_file=20, error_rate=0.05)

    # Benchmark error rate
    benchmark_dimension('error_rate', [0.01, 0.05, 0.1,0.15,0.2], base_path,base_path_test,
                        num_files=5, rows_per_file=100, columns_per_file=20, data_complexity=3)

    print("Benchmarking complete. Results have been saved as PNG files.")