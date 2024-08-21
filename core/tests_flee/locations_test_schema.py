
import pandera as pa
from pandera.typing import Series

class LocationsTestScheme(pa.DataFrameModel):
    name: Series[str] = pa.Field(nullable=False)
    region: Series[str] = pa.Field()
    country: Series[str] = pa.Field()
    latitude: Series[float] = pa.Field(ge=-90, le=90)
    longitude: Series[float] = pa.Field(ge=-180, le=180)
    location_type: Series[str] = pa.Field(isin=["conflict_zone", "town", "camp", "forwarding_hub", "marker", "idpcamp"])
    conflict_date: Series[float] = pa.Field(nullable=True, ge=0)
    population: Series[float] = pa.Field(ge=0, nullable=True)
    extra_col_8: Series[float] = pa.Field(nullable=True)
extra_col_9: Series[int] = pa.Field(nullable=True)
extra_col_10: Series[int] = pa.Field(nullable=True)
extra_col_11: Series[float] = pa.Field(nullable=True)
extra_col_12: Series[str] = pa.Field()
extra_col_13: Series[str] = pa.Field()
extra_col_14: Series[float] = pa.Field(nullable=True)
extra_col_15: Series[str] = pa.Field()
extra_col_16: Series[float] = pa.Field(nullable=True)
extra_col_17: Series[int] = pa.Field(nullable=True)
extra_col_18: Series[float] = pa.Field(nullable=True)
extra_col_19: Series[float] = pa.Field(nullable=True)
