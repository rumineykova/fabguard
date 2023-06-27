# FabGuard

FabGuard is a tool that helps verify input files by specifying constraints on the data. This is a first iteration where 
we are collecting at the type of constraints in various simulation input files and deriving the tool requirements. 
As a first exercise, we are testing a library for data validation of Panda Dataframes, called [pandera](https://github.com/unionai-oss/pandera). 

## Installation

To install FabGuard, follow these steps:

1. Clone the FabGuard repository:

2. Install the required dependencies:

```
pip install pandera
```

## Test examples

1. Test the examples in the `test_pandera.py` file to familiarise yourself with the capabilities of the library.
`test_pandera.py` demonstrate how to test three type of constraints:
  - **simple constraints on columns**. 
    The function below can check the following simple constraint: 
    - *population* > 0 
    - *location_type* shouldhave one of the following values "conflict_zone", "town", "camp", "forwarding_hub"
    ```  python
    def validate_simple_constraints():
        schema = pa.DataFrameSchema(
            {
                "population": Column(float, Check.greater_than(10), nullable=True),
                "location_type": Column(str, Check.isin(["conflict_zone", "town", "camp", "forwarding_hub"])),
            }
        )
    
        return schema 
    ```
  - **constraints spanning multiple columns from the same file**
   The function below can check the following constraint using a lambda function: 
    - if location_type == "conflict_zone" then population > 0 
    ```python
    def validate_two_dependent_columns():
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
    ```
  - **constarints spanning multiple files**


2. You can check other examples in `test_pandera.py`

###  How-to: Test on your own dataset:
   
1. Define a verify function that returns a pandera schema
Examples of such functions are the functions given in the Test examples section
`validate_simple_constraints`  

2 Call the `validator.validate` function with the above function and the data frame to be verified:
       
```python 
dfs = util.load_files(["test_data/locations.csv", "test_data/closures.csv"])
validator.validate(validate_simple_constraints, dfs["closures"], "verify_multi.yaml")
```
   where
   - `util.load_files` reads the list of files and returns a dictionary of dataframes
   - `validator.validate`takes a validation function, a dataframe, and a yaml output file

###  List of requirements 
- metrics across different runs
- count function on columns: the value of one column should be the size of a column in one file should be 
    - conflict_period.length = size(closures.day)
- ✓ All cities in location.csv should have routes in routes.csv (location.name should be in routes.name1 or routes.name2)
    - If locations.location_type == camp then 
        location.name in routes.name1  or location.name is routes.name2
- ✓ The number of records in location_type is X then data_laypout file contains a linked record:
    -  if location.location_type == camp then 
        - Location.name in data_layout.total and data_layout.name is nonempty.

- All columns but one should satisfy the same constraint 
- ✓ All data exists, min-max, All regions have positive values 
- Check scheme (such that yaml does not break w.r.t identation)

