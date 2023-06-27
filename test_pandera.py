import pandera as pa
import pandas as pd
from pandera import Column, Check, extensions
from typing import Dict
import validator
import util


"""
Example of a custom verification function over multiple columns
can be used to check the following constraint
if locations.location_type == "conflict":
    require locations.pop > 0
where group_a is the location_type column with a value conflict
and the constraints is that population is > 0, represented below as 
dict_groups[group_a] >0
"""
@extensions.register_check_method(
    statistics=["group_a"],
    check_type="groupby"
)
def groupby_check(dict_groups: Dict[str, pd.Series], *, group_a):
    print(dict_groups)
    return dict_groups[group_a] > 5

"""
The function below can check the following constraint using a lambda function: 
-if location_type == "conflict_zone":
    require population > 0
"""
def validate_dependencies_multiple_columns():
    schema = pa.DataFrameSchema(
        {
            "population": pa.Column(float, [
                pa.Check(
                    lambda g: g["conflict_zone"] > 0,
                    groupby=["location_type"])], nullable=True, coerce=True),
            "location_type": Column(str, Check.isin(["conflict_zone", "town", "camp", "forwarding_hub"])),
        }
    )

    return schema

"""
The function below can check the following constraints using a custom defined function: 
-if location_type == "conflict":
    require population > 0
"""
def validate_if_location():
    schema = pa.DataFrameSchema(
        {
            "population": pa.Column(float, [
                pa.Check.groupby_check(group_a="conflict_zone",groupby="location_type")], nullable=True, coerce=True),
            "location_type": Column(str, Check.isin(["conflict_zone", "town", "camp", "forwarding_hub"]))
        }
    )

    return schema

"""
The function below can check the following simple constraint: 
- population > 0
- location_type shouldhave one of the following values "conflict_zone", "town", "camp", "forwarding_hub
"""
def validate_simple_constarints():
    schema = pa.DataFrameSchema(
        {
            "population": Column(float, Check.less_than(10), nullable=True),
            "location_type": Column(str, Check.isin(["conflict_zone", "town", "camp", "forwarding_hub"])),
        }
    )

    return schema


# assume we have locations, and closures df which are merged?


"""
The function below can check the following simple constraint: 
if closures.closure == "location":
    closures.name1 in locations.name
    closures.name2 in locations.names
where closure and locations are different input files 
"""
def validate_dependencies_multiple_files():
    df = util.load_file("test_data/locations.csv")
    location_names = df["#name"]

    schema = pa.DataFrameSchema(
        columns={
            "name1": pa.Column(str),
            "name2": pa.Column(str),
            "closure": pa.Column(str)
        },
        checks = [
            pa.Check(lambda df: df.loc[df["closure"] == "location", "name1"].isin(location_names)),
            pa.Check(lambda df: df.loc[df["closure"] == "location", "name2"].isin(location_names))
        ]
    )

    return schema


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dfs = util.load_files(["test_data/locations.csv", "test_data/closures.csv"])
    validator.validate(validate_dependencies_multiple_files, dfs["closures"], "verify_multi.yaml")
    validator.validate(validate_dependencies_multiple_columns, dfs["locations"], "verify_multi.yaml")
    validator.validate(validate_dependencies_multiple_columns, dfs["locations"], "verify_multi.yaml")