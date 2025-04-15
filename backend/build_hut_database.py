import json
import os
from typing import Text, Tuple
import numpy as np
from scipy.spatial.distance import cdist
import geopandas as gpd
import googlemaps
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlemaps import Client as GoogleMaps

PLACES_CODE = "total sleeping places: "
WARDEN_CODE = "hut warden(s): "
ALT_CODE = "height above sea level: "
COORDS_CODE = "coordinates: "
PHONE_CODE = "Hut phone number: "
ALPENVEREIN_SHORTCUTS = ["DAV", "SAC", "Genossenschaft", "Alpenverein", "AVS", "ÖAV", "CAS"]
DATA_PATH = "data"
# os.makedirs(DATA_PATH, exist_ok=True)
GM_CLIENT = GoogleMaps(open("gpc_api_key.keypair", "r").read())


def get_coordinates(title: str, api: googlemaps.client.Client) -> Tuple[float, float]:
    """
    Perform geolocationing for a title and a subtitle.

    Args:
        title: Title of the penny machine.
        subtitle: Subtitle of the penny machine.
        api: google maps API object.

    Returns:
        Tuple[float, float]: Latitude and longitude
    """

    # Make GM request, default title and subtitle.
    queries = [title]

    for query in queries:
        coordinates = api.geocode(query)

        try:
            lat = coordinates[0]["geometry"]["location"]["lat"]
            lng = coordinates[0]["geometry"]["location"]["lng"]
            break
        except IndexError:
            continue
    try:
        lat
    except NameError:
        print(f"Geolocation failed for: {title}")
        lat, lng = pd.NA, pd.NA
    return lat, lng


def find_verein(hut: Text) -> Tuple:
    found_verein = False
    for verein in ALPENVEREIN_SHORTCUTS:
        name_and_verein = hut.split(verein)
        if len(name_and_verein) > 1:
            hut_name_short = name_and_verein[0].replace(", ", "")
            hut_verein = verein
            specific_verein = name_and_verein[-1].replace(",", "")
            found_verein = True
            break
    if not found_verein:
        return hut, None, None
    return hut_name_short, hut_verein, specific_verein


def crawl_general_info(out_path: str, final_out_path: str):
    # path to save raw json files
    os.makedirs(out_path, exist_ok=True)

    all_huts_info = []

    for hut_id in range(680):
        out_file = os.path.join(out_path, f"{hut_id}.json")
        # First step: check if generally available
        url = f"https://www.alpsonline.org/reservation/calendar?hut_id={hut_id}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"status code {response.status_code} - skip")
            continue
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")  # , "lxml")

        hut_name = soup.find("h4").text

        hut_meta_info = {"id": hut_id, "name_original": hut_name}

        # retrieve hut information
        for span_elem in soup.find_all("span"):
            info_text = span_elem.text.lower()
            if "warden" in info_text:
                hut_meta_info["hut_warden"] = info_text.replace(WARDEN_CODE, "")
            elif "places" in info_text:
                hut_meta_info["total_places"] = info_text.replace(PLACES_CODE, "")
            elif "height" in info_text:
                hut_meta_info["altitude"] = info_text.replace(ALT_CODE, "")
            elif "coordinates" in info_text:
                hut_meta_info["coordinates"] = info_text.replace(COORDS_CODE, "")
            elif "phone" in info_text:
                hut_meta_info["phone"] = info_text.replace(PHONE_CODE, "")

        # get short hut name and alpenverein
        hut_name_short, hut_verein, specific_verein = find_verein(hut_name)
        hut_meta_info["name"] = hut_name_short
        hut_meta_info["verein"] = hut_verein
        hut_meta_info["sektion"] = specific_verein

        # save meta info
        with open(out_file, "w") as outf:
            json.dump(hut_meta_info, outf, ensure_ascii=False)

        all_huts_info.append(hut_meta_info)
        print(f"saved meta info of {hut_name}")

    all_huts_info = pd.DataFrame(all_huts_info).set_index("id")
    all_huts_info.to_csv(final_out_path)


def call_maps_api(row):
    hut_name = row["name"]
    verein = row["verein"]
    if pd.isna(hut_name):
        row["latitude"] = None
        row["longitude"] = None
        return row
    elif pd.isna(verein):
        gm_input = hut_name
    else:
        gm_input = hut_name + ", " + verein
    lat, lon = get_coordinates(gm_input, GM_CLIENT)
    row["latitude"] = lat
    row["longitude"] = lon
    return row


def get_alt_meter(alt: Text) -> int:
    """
    Retrieve altitude from NNNNm csv column.

    Args:
        alt: altitude csv column test in format NNNNm

    Returns:
        alt_int: altitude converted to int
    """

    try:
        alt_int = float(alt.replace("m", ""))
    except ValueError:
        alt_int = pd.NA
    except AttributeError:
        alt_int = pd.NA
    return alt_int


def get_places_cleaned(places: Text) -> int:
    """
    Clean places column and try to convert to int.

    Args:
        places: place text from csv

    Returns:
        places_int: places column as int
    """

    try:
        places_int = int(places)
    except ValueError:
        parts = places.split(" ")
        places_int = 10
        for p in parts:
            try:
                places_int = int(p)
                break
            except ValueError:
                continue
    return places_int


def clean_huts(inp_path, out_path):
    huts_gdf = gpd.read_file(inp_path, index_col="id").dropna(subset="name").drop("Unnamed: 0", axis=1)
    huts_gdf["altitude_m"] = huts_gdf["altitude"].apply(get_alt_meter)
    huts_gdf["total_places"] = huts_gdf["total_places"].apply(get_places_cleaned).astype(int)
    huts_gdf_clean = huts_gdf.dropna(subset=["altitude_m"])
    huts_gdf_clean["altitude_m"] = huts_gdf_clean["altitude_m"].astype(float)
    huts_gdf_clean.to_file(out_path, driver="GeoJSON")


def save_feasible_connections(max_distance: int = 10000):
    """Generate all feasible connections between huts and save to csv."""
    huts = gpd.read_file(os.path.join("data", "huts_database.geojson"))
    huts.to_crs(2421, inplace=True)
    hut_coords = np.stack([huts.geometry.x, huts.geometry.y]).T
    pairwise_dist = cdist(hut_coords, hut_coords)

    # create a mask for the distances
    is_connected = (pairwise_dist <= max_distance) & (pairwise_dist > 0)
    ids = huts["id"].values
    # iterate over combinations and add them to df
    combs = []
    nr_huts = len(is_connected)
    for i in range(nr_huts):
        for j in range(nr_huts):
            if is_connected[i, j]:
                combs.append({"id_source": ids[i], "id_target": ids[j], "distance": int(pairwise_dist[i, j])})
    feasible_connections = pd.DataFrame(combs).set_index("id_source")
    feasible_connections.to_csv(os.path.join("data", "feasible_connections.csv"))


if __name__ == "__main__":
    # set paths
    raw_out_path = os.path.join(DATA_PATH, "raw")
    hut_info_out_path = os.path.join(DATA_PATH, "hut_info.csv")
    hut_coord_out_path = os.path.join(DATA_PATH, "hut_coords.csv")
    hut_coord_geojson = os.path.join(DATA_PATH, "huts_gdf.geojson")
    hut_final_cleaned = os.path.join(DATA_PATH, "huts_database.geojson")

    # Crawl info
    crawl_general_info(raw_out_path, hut_info_out_path)

    # load hut info and use gogle maps API
    hut_info = pd.read_csv(hut_info_out_path)
    hut_info_with_coords = hut_info.apply(call_maps_api, axis=1)
    hut_info_with_coords.to_csv(hut_coord_out_path)

    # transform into geojson
    hut_info_with_coords = pd.read_csv(hut_coord_out_path)
    huts_gdf = gpd.GeoDataFrame(
        hut_info_with_coords,
        geometry=gpd.points_from_xy(x=hut_info_with_coords["longitude"], y=hut_info_with_coords["latitude"]),
    )
    huts_gdf.crs = "4326"
    huts_gdf.to_file(hut_coord_geojson, driver="GeoJSON")

    # clean ups
    clean_huts(hut_coord_geojson, hut_final_cleaned)

    # save feasible connections
    save_feasible_connections()
