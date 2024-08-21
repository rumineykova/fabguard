import pandas as pd
import numpy as np
import random
from faker import Faker

fake = Faker()


def generate_synthetic_locations(num_rows, num_columns, error_rate=0.05):
    data = {
        'name': [fake.city() for _ in range(num_rows)],
        'region': [fake.state() for _ in range(num_rows)],
        'country': ['Ethiopia' for _ in range(num_rows)],
        'latitude': [fake.latitude() for _ in range(num_rows)],
        'longitude': [fake.longitude() for _ in range(num_rows)],
        'location_type': np.random.choice(['conflict_zone', 'town', 'camp', 'forwarding_hub', 'marker', 'idpcamp'],
                                          num_rows),
        'conflict_date': [random.randint(0, 100) if random.random() < 0.7 else None for _ in range(num_rows)],
        'population': [random.randint(1000, 1000000) for _ in range(num_rows)]
    }

    # Add extra columns if needed
    for i in range(8, num_columns):
        data[f'extra_column_{i}'] = [fake.word() for _ in range(num_rows)]

    df = pd.DataFrame(data)

    # Introduce errors based on error_rate
    num_errors = int(num_rows * error_rate)
    for _ in range(num_errors):
        row = random.randint(0, num_rows - 1)
        col = random.choice(list(data.keys()))
        if col == 'name':
            df.at[row, col] = ''
        elif col == 'latitude' or col == 'longitude':
            df.at[row, col] = random.uniform(-1000, 1000)
        elif col == 'location_type':
            df.at[row, col] = 'invalid_type'
        elif col == 'conflict_date':
            df.at[row, col] = -1
        elif col == 'population':
            df.at[row, col] = -1000

    return df


def generate_multiple_files(num_files, rows_per_file, columns_per_file, base_path, error_rate=0.05):
    for i in range(num_files):
        df = generate_synthetic_locations(rows_per_file, columns_per_file, error_rate)
        df.to_csv(f"{base_path}/synthetic_locations_{i + 1}.csv", index=False)


# Example usage
generate_multiple_files(num_files=10, rows_per_file=1000, columns_per_file=10, base_path="./synthetic_data",
                        error_rate=0.05)


def generate_constraints(num_constraints):
    constraints = [
        "@pa.check('name', element_wise=True)\n"
        "def check_name(cls, name):\n"
        "    return len(name) > 0\n",

        "@pa.check('latitude', element_wise=True)\n"
        "def check_latitude(cls, lat):\n"
        "    return -90 <= lat <= 90\n",

        "@pa.check('longitude', element_wise=True)\n"
        "def check_longitude(cls, lon):\n"
        "    return -180 <= lon <= 180\n",

        "@pa.check('population', element_wise=True)\n"
        "def check_population(cls, pop):\n"
        "    return pop >= 0\n",

        "@pa.check('conflict_date', element_wise=True)\n"
        "def check_conflict_date(cls, date):\n"
        "    return date is None or date >= 0\n"
    ]

    # Generate additional dummy constraints if needed
    for i in range(len(constraints), num_constraints):
        constraints.append(
            f"@pa.check('extra_column_{i}', element_wise=True)\n"
            f"def check_extra_column_{i}(cls, value):\n"
            f"    return len(str(value)) > 0\n"
        )

    return constraints[:num_constraints]


def generate_pandera_schema(num_columns, num_constraints):
    schema = "import pandera as pa\n\n"
    schema += "class LocationsScheme(pa.DataFrameModel):\n"

    # Add column definitions
    columns = [
        "name", "region", "country", "latitude", "longitude",
        "location_type", "conflict_date", "population"
    ]
    for col in columns:
        schema += f"    {col}: pa.Column(pa.String)\n"

    # Add extra columns if needed
    for i in range(8, num_columns):
        schema += f"    extra_column_{i}: pa.Column(pa.String)\n"

    # Add constraints
    constraints = generate_constraints(num_constraints)
    for constraint in constraints:
        schema += "\n" + constraint

    return schema


# Example usage
schema = generate_pandera_schema(num_columns=10, num_constraints=7)
with open("synthetic_locations_schema.py", "w") as f:
    f.write(schema)

print("Synthetic data and schema generated successfully!")