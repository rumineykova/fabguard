# Example usage of the LAMMPS parser and validator
from pathlib import Path

from main import validate_lammps_file

valid_input = """
# Valid LAMMPS input
units       lj
dimension   3
mass        1 1.0
mass        2 1.0
pair_style  lj/cut 2.5
pair_coeff  1 1 1.0 1.0 2.5
"""

invalid_input = """
# Invalid LAMMPS input with errors
units       invalid_unit
dimension   4
mass        1 -1.0
pair_coeff  1 1 1.0 1.0  # Missing pair_style
"""

# Test valid input
print("Validating correct input:")
input = Path('LAMMPS.txt').read_text()
errors = validate_lammps_file(input)
if not errors:
    print("No errors found")
else:
    print("\n".join(errors))


print("\nValidating incorrect input:")
errors = validate_lammps_file(invalid_input)
if errors:
    print("\n".join(errors))
