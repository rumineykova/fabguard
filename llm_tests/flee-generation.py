import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Float, DateTime
from datetime import datetime
from geopy.distance import geodesic

class LocationsScheme(pa.DataFrameModel):
    # Ensure each location has a unique, non-null name
    name: Series[String] = pa.Field(nullable=False, unique=True)
    # Region is a string field with no specific constraints
    region: Series[String] = pa.Field()
    # Country is a string field
    country: Series[String] = pa.Field()
    # Latitude must be between -90 and 90 degrees
    lat: Series[Float] = pa.Field(ge=-90, le=90)
    # Longitude must be between -180 and 180 degrees
    lon: Series[Float] = pa.Field(ge=-180, le=180)
    # Location type must be one of the predefined types
    location_type: Series[String] = pa.Field(isin=["conflict_zone", "town", "camp", "forwarding_hub", "marker", "idpcamp"])
    # Conflict date can be null for non-conflict zones
    conflict_date: Series[DateTime] = pa.Field(nullable=True)
    # Population must be non-negative
    population: Series[Float] = pa.Field(ge=0)
    # Maximum capacity of the location (can be null)
    max_capacity: Series[Float] = pa.Field(nullable=True)

    @pa.check("name")
    def name_exists_in_routes(cls, name: str, routes_df: pd.DataFrame) -> bool:
        """Constraint: Ensure each location name exists in the routes file."""
        all_route_locations = set(routes_df["name1"]).union(set(routes_df["name2"]))
        return name in all_route_locations

    @pa.check("lat", "lon")
    def not_on_null_island(cls, lat: float, lon: float) -> bool:
        """Constraint: Ensure coordinates are not on or very close to null island (0,0)."""
        return not (abs(lat) < 0.001 and abs(lon) < 0.001)

    @pa.check("conflict_date")
    def conflict_date_for_conflict_zone(cls, conflict_date, location_type):
        """Constraint: Ensure conflict zones have a conflict date, and other locations do not."""
        return pd.isna(conflict_date) if location_type != "conflict_zone" else not pd.isna(conflict_date)

    @pa.check("population")
    def population_constraints(cls, population, location_type, max_capacity):
        """Constraint: Enforce population rules based on location type and max capacity."""
        if location_type in ["conflict_zone", "town", "camp"]:
            return 0 < population <= max_capacity if pd.notna(max_capacity) else population > 0
        elif location_type == "marker":
            return population == 0
        elif location_type == "forwarding_hub":
            return population >= 0
        return True

    @pa.dataframe_check
    def country_consistent_for_conflict_zones(cls, df):
        """Constraint: Ensure all conflict zones are in the same country."""
        conflict_zones = df[df["location_type"] == "conflict_zone"]
        return conflict_zones["country"].nunique() == 1

    @pa.dataframe_check
    def conflict_dates_order(cls, df):
        """Constraint: Ensure conflict dates are in chronological order."""
        conflict_zones = df[df["location_type"] == "conflict_zone"].sort_values("conflict_date")
        return (conflict_zones["conflict_date"].diff()[1:] >= pd.Timedelta(days=0)).all()

class RoutesScheme(pa.DataFrameModel):
    # Each route must have a non-null starting location
    name1: Series[String] = pa.Field(nullable=False)
    # Each route must have a non-null ending location
    name2: Series[String] = pa.Field(nullable=False)
    # Distance between locations must be non-negative
    distance: Series[Float] = pa.Field(ge=0)
    # Forced redirection can be null (optional field)
    forced_redirection: Series[String] = pa.Field(nullable=True)

    @pa.dataframe_check
    def locations_exist(cls, routes_df, locations_df):
        """Constraint: Ensure all locations in routes exist in the locations file."""
        all_locations = set(locations_df["name"])
        all_route_locations = set(routes_df["name1"]).union(set(routes_df["name2"]))
        return all_route_locations.issubset(all_locations)

    @pa.dataframe_check
    def route_consistency(cls, routes_df):
        """Constraint: Ensure routes are bidirectional (if A to B exists, B to A should also exist)."""
        forward_routes = set(zip(routes_df["name1"], routes_df["name2"]))
        backward_routes = set(zip(routes_df["name2"], routes_df["name1"]))
        return forward_routes == backward_routes

    @pa.dataframe_check
    def geographical_distance_check(cls, routes_df, locations_df):
        """Constraint: Ensure route distances are reasonably close to calculated geographical distances."""
        for _, route in routes_df.iterrows():
            loc1 = locations_df[locations_df["name"] == route["name1"]].iloc[0]
            loc2 = locations_df[locations_df["name"] == route["name2"]].iloc[0]
            geo_distance = geodesic((loc1["lat"], loc1["lon"]), (loc2["lat"], loc2["lon"])).kilometers
            if abs(geo_distance - route["distance"]) > 10:  # Allow 10 km discrepancy
                return False
        return True

def validate_flee_data(locations_file, routes_file):
    """Validate both locations and routes data against the defined schemas."""
    locations_df = pd.read_csv(locations_file, parse_dates=["conflict_date"])
    routes_df = pd.read_csv(routes_file)

    # We need to pass routes_df to LocationsScheme for the name check
    validated_locations = LocationsScheme.validate(locations_df, routes_df=routes_df)
    validated_routes = RoutesScheme.validate(routes_df, locations_df=locations_df)

    print("Data validation successful!")
    return validated_locations, validated_routes

# Usage:
# validated_locations, validated_routes = validate_flee_data("locations.csv", "routes.csv")
