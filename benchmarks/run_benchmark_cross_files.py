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
    # Existing function remains the same
    ...


def generate_synthetic_routes(num_rows, locations_df):
    routes = []
    for _ in range(num_rows):
        start = np.random.choice(locations_df['name'])
        end = np.random.choice(locations_df['name'])
        while end == start:
            end = np.random.choice(locations_df['name'])
        routes.append({'name1': start, 'name2': end})
    return pd.DataFrame(routes)


def generate_multiple_files(num_files, rows_per_file, columns_per_file, base_path, data_complexity, error_rate):
    for i in range(num_files):
        folder_path = os.path.join(base_path, f"test_folder_{i + 1}/input_csv")
        os.makedirs(folder_path, exist_ok=True)

        # Generate locations
        locations_df = generate_synthetic_locations(rows_per_file, columns_per_file, data_complexity, error_rate)
        locations_df.to_csv(os.path.join(folder_path, 'locations.csv'), index=False)

        # Generate routes based on locations
        routes_df = generate_synthetic_routes(rows_per_file // 2, locations_df)
        routes_df.to_csv(os.path.join(folder_path, 'routes.csv'), index=False)

        # Create empty closures file
        open(os.path.join(folder_path, 'closures.csv'), 'w').close()


def generate_cross_file_constraints(num_constraints):
    constraints = []
    for i in range(num_constraints):
        constraint = f"""
    @pa.check("name1")
    def check_route_start(cls, series):
        locations_df = pd.read_csv("locations.csv")
        return series.isin(locations_df['name'])

    @pa.check("name2")
    def check_route_end(cls, series):
        locations_df = pd.read_csv("locations.csv")
        return series.isin(locations_df['name'])
        """
        constraints.append(constraint)
    return "\n".join(constraints)


def generate_pandera_schema(num_columns, data_complexity, num_cross_file_constraints):
    locations_schema = """
import pandera as pa
from pandera.typing import Series
import pandas as pd

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

    routes_schema = """
class RoutesTestScheme(pa.DataFrameModel):
    name1: Series[str] = pa.Field(nullable=False)
    name2: Series[str] = pa.Field(nullable=False)
    """

    routes_schema += generate_cross_file_constraints(num_cross_file_constraints)

    return locations_schema, routes_schema


def run_benchmark(base_path, base_path_test, num_files, rows_per_file, columns_per_file, data_complexity, error_rate,
                  num_cross_file_constraints):
    generate_multiple_files(num_files, rows_per_file, columns_per_file, base_path, data_complexity, error_rate)

    locations_schema, routes_schema = generate_pandera_schema(columns_per_file, data_complexity,
                                                              num_cross_file_constraints)

    with open(os.path.join(base_path_test, 'locations_test_schema.py'), 'w') as f:
        f.write(locations_schema)

    with open(os.path.join(base_path_test, 'routes_test_schema.py'), 'w') as f:
        f.write(routes_schema)

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024
    peak_memory = initial_memory

    start_time = time.time()

    for i in range(num_files):
        folder_name = f"test_folder_{i + 1}"
        command = f"fabsim localhost flee_verify_input:{folder_name}"
        subprocess.run(command, shell=True, check=True)

        current_memory = process.memory_info().rss / 1024 / 1024
        peak_memory = max(peak_memory, current_memory)

    end_time = time.time()

    execution_time = end_time - start_time
    memory_used = max(0, peak_memory - initial_memory)

    return execution_time, memory_used


def benchmark_dimension(dimension_name, dimension_values, base_path, base_path_test, num_runs=5, warmup_runs=3,
                        **fixed_params):
    # Existing function remains largely the same, but pass num_cross_file_constraints to run_benchmark
    ...


if __name__ == "__main__":
    base_path = "/Users/rumyananeykova/Dev/FabSim3/plugins/FabFlee/config_files/"
    base_path_test = "/Users/rumyananeykova/Dev/FabSim3/plugins/FabFlee/fab_guard/tests"
    os.makedirs(base_path, exist_ok=True)

    # Existing benchmarks remain the same

    # New benchmark for cross-file constraints
    benchmark_dimension('num_cross_file_constraints', [1, 2, 5, 10, 20], base_path, base_path_test,
                        num_files=5, rows_per_file=1000, columns_per_file=20, data_complexity=3, error_rate=0.05)

    print("Benchmarking complete. Results have been saved as PNG files.")