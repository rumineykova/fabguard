import util
import pandera as pa

def validate(schema_generator, df, output_file):
    schema = schema_generator()
    res = schema.validate(df)
    yaml_schema = schema.to_yaml()
    yaml_schema.replace(f"{pa.__version__}", "{PANDERA_VERSION}")
    util.write_to_file(output_file, yaml_schema)
    print(res)



