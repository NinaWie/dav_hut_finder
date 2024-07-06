"""This file is for demonstration purposes and will be removed (or replaced by a proper test class)"""

import os
import geopandas as gpd
from filtering import filter_huts

if __name__ == "__main__":
    huts = gpd.read_file(os.path.join("data", "huts_database.geojson"))

    # start from munich
    start_lat, start_lon = 48.1381528, 11.5762854
    # maximal 150 km
    max_distance = 150

    # filter huts
    filtered = filter_huts(huts, min_altitude=1000, start_lat=start_lat, start_lon=start_lon, max_distance=max_distance)
    print(filtered.sort_values("distance"))
