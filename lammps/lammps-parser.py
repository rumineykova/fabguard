from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class CommandType(Enum):
    UNITS = "units"
    DIMENSION = "dimension"
    MASS = "mass"
    PAIR_STYLE = "pair_style"
    PAIR_COEFF = "pair_coeff"
    # Add other commands as needed

@dataclass
class Command:
    type: CommandType
    parameters: List[str]
    line_number: int

class LAMMPSParser:
    def parse(self, content: str) -> List[Command]:
        """Parse LAMMPS input file content into Command objects."""
        commands = []
        for i, line in enumerate(content.split('\n'), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if not parts:
                continue
                
            try:
                cmd_type = CommandType(parts[0])
                commands.append(Command(
                    type=cmd_type,
                    parameters=parts[1:],
                    line_number=i
                ))
            except ValueError:
                # Unknown command type - could log warning here
                continue
                
        return commands

class LAMMPSValidator:
    def __init__(self):
        self.valid_units = {"lj", "real", "metal"}
        self.defined_atom_types = set()
        self.pair_style_defined = False
    
    def validate_command(self, cmd: Command) -> List[str]:
        """Validate a single command, returns list of error messages."""
        errors = []
        
        if cmd.type == CommandType.UNITS:
            if len(cmd.parameters) != 1:
                errors.append(f"Line {cmd.line_number}: Units command requires exactly one parameter")
            elif cmd.parameters[0] not in self.valid_units:
                errors.append(f"Line {cmd.line_number}: Invalid units type '{cmd.parameters[0]}'")
                
        elif cmd.type == CommandType.DIMENSION:
            if len(cmd.parameters) != 1:
                errors.append(f"Line {cmd.line_number}: Dimension command requires exactly one parameter")
            try:
                dim = int(cmd.parameters[0])
                if dim not in {2, 3}:
                    errors.append(f"Line {cmd.line_number}: Dimension must be 2 or 3")
            except ValueError:
                errors.append(f"Line {cmd.line_number}: Dimension must be an integer")
                
        elif cmd.type == CommandType.MASS:
            if len(cmd.parameters) != 2:
                errors.append(f"Line {cmd.line_number}: Mass command requires exactly two parameters")
            else:
                try:
                    atom_type = int(cmd.parameters[0])
                    mass = float(cmd.parameters[1])
                    if mass <= 0:
                        errors.append(f"Line {cmd.line_number}: Mass must be positive")
                    self.defined_atom_types.add(atom_type)
                except ValueError:
                    errors.append(f"Line {cmd.line_number}: Invalid mass specification")
                    
        elif cmd.type == CommandType.PAIR_STYLE:
            if len(cmd.parameters) < 1:
                errors.append(f"Line {cmd.line_number}: Pair style command requires at least one parameter")
            self.pair_style_defined = True
            
        elif cmd.type == CommandType.PAIR_COEFF:
            if not self.pair_style_defined:
                errors.append(f"Line {cmd.line_number}: Pair coefficients defined before pair style")
            if len(cmd.parameters) < 4:
                errors.append(f"Line {cmd.line_number}: Pair coeff command requires at least 4 parameters")
            else:
                try:
                    type1, type2 = int(cmd.parameters[0]), int(cmd.parameters[1])
                    if type1 not in self.defined_atom_types or type2 not in self.defined_atom_types:
                        errors.append(f"Line {cmd.line_number}: Undefined atom type in pair coefficients")
                except ValueError:
                    errors.append(f"Line {cmd.line_number}: Invalid atom types in pair coefficients")
                    
        return errors

def validate_lammps_file(content: str) -> List[str]:
    """Main function to validate a LAMMPS input file."""
    parser = LAMMPSParser()
    validator = LAMMPSValidator()
    
    commands = parser.parse(content)
    all_errors = []
    
    for cmd in commands:
        errors = validator.validate_command(cmd)
        all_errors.extend(errors)
        
    return all_errors
