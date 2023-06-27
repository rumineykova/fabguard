import pandas as pd
import pandera as pa
import os

def load_file(file):
    df = pd.read_csv(file)
    return df


def infer_scheme(df):
    schema = pa.infer_schema(df)
    return schema


def write_to_file(file, text):
    with open(file, "w") as file1:
        # Writing data to a file
        file1.write(text)


def generate_test_df():
    locations = pd.DataFrame(
        {
            "population": [6, 0, 1, 2],
            "location_type": ["conflict_zone", "town", "camp", "town"],
            "latitude": [1, 2, 3, 4],
            "#name": ["a", "b", "c", "d"]
        }
    )

    closures = pd.DataFrame(
        {
            "name1": ["c", "d", "d", "a"],
            "name2": ["a", "e", "b", "f"],
            "closure": ["location", "migration", "location", "migration"]
        }
    )

    return {"locations":locations, "closures": closures}

"""
Read a list of csv files as dataframes
returns a dictionary: FileName -> Dataframe 
"""
def load_files(files):
    d = dict()
    for file in files:
        df = pd.read_csv(file)
        name = os.path.splitext(os.path.basename(file))[0]
        d[name] = df
    return d
