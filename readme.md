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
3. Test the examples in the `test_pandera.py` file to familiarise yourself with the capabilities of the library.
`test_pandera.py` demonstrate how to test three type of constraints:
  - simple constarints on columns
  - constarints spanning multipple columns from the same file
  - constarints spanning multiple files 
   3.1
    
5. Test it on your own dataset:
  5.1 Define a verify function that returns a pandera schema
  5.2 Call the `validator.validate` function with the above function and the data frame to be verified:
   ```
   dfs = util.load_files(["test_data/locations.csv", "test_data/closures.csv"])
   validator.validate(validate_multi, dfs["closures"], "verify_multi.yaml")
   ```
   where
   - `util.load_files` reads the list of files and returns a dictionary of dataframes
   - `validator.validate`takes a validation function, a dataframe, and a yaml output file

