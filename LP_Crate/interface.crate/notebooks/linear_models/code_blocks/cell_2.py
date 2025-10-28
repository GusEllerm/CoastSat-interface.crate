# Transects, origin is landward. Has beach_slope
transects = gpd.read_file("transects_extended.geojson")
transects.set_index("id", inplace=True)
transects