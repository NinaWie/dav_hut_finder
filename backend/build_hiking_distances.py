"""One-time script to compute real hiking-trail distances between huts.

Produces data/hiking_distances.csv: every hut pair within MAX_BEELINE_DISTANCE_M (haversine)
with its beeline distance, plus hiking-trail distance and cumulative ascent/descent (meters, from
SRTM elevation data) for pairs that have an actual, plausible trail route. Pairs that would
require off-trail/glacier travel (no mapped route, or only an absurd valley-road detour) keep
empty hiking columns -- the app only routes over them when the user opts into beeline distance,
rather than silently mixing the two.

Usage:
    python build_hiking_distances.py

Requires (only for this script, not for the Flask app):
    - pip packages: pyrosm, python-igraph, scikit-learn, srtm.py (see the "routing" extra in
      pyproject.toml)
    - the `osmium` CLI (e.g. `brew install osmium-tool`) to pre-filter the OSM extract
"""

import os
import subprocess

import geopandas as gpd
import igraph
import numpy as np
import pandas as pd
import requests
import srtm
from pyrosm import OSM
from sklearn.neighbors import BallTree

DATA_PATH = "data"
RAW_PATH = os.path.join(DATA_PATH, "raw")
OSM_EXTRACT_URL = "https://download.geofabrik.de/europe/alps-latest.osm.pbf"
OSM_EXTRACT_PATH = os.path.join(RAW_PATH, "alps-latest.osm.pbf")
GRAPH_CACHE_PATH = os.path.join(RAW_PATH, "walking_graph.pkl")
GRAPH_NODES_CACHE_PATH = os.path.join(RAW_PATH, "walking_graph_nodes.csv")
HIKING_WAYS_PATH = os.path.join(RAW_PATH, "alps-hiking.osm.pbf")
# pure trail tags plus the small-road tags that commonly bridge separate trail networks in the
# mountains (village streets, forestry/service roads); without these the trail-only network is
# heavily fragmented into disconnected islands and most hut-to-hut routes fail to resolve
HIKING_HIGHWAY_TAGS = [
    "path",
    "track",
    "footway",
    "steps",
    "bridleway",
    "unclassified",
    "service",
    "living_street",
    "road",
]

EARTH_RADIUS_M = 6_371_000
# candidate hut pairs are those within this straight-line distance (good hikers can cover up to
# ~30km/day, so 20km beeline leaves good margin for the actual trail distance to still be hikeable)
MAX_BEELINE_DISTANCE_M = 20_000
# snap distances larger than this indicate the hut is far from any mapped trail (bad geocode etc.)
MAX_SNAP_DISTANCE_M = 2000
# some hut pairs are only reachable via glacier/off-trail terrain with no mapped path between them;
# the router then finds a real but absurd valley-road detour instead. Such pairs are excluded from
# the output entirely rather than reporting an implausible hiking distance (see module docstring).
MAX_DETOUR_RATIO = 6
MAX_DETOUR_FLOOR_M = 15_000
# resample the path to this spacing before looking up elevations: DEM grid noise gets amplified
# into spurious ascent/descent if we sample every (densely spaced) path node directly.
# Calibrated against a known Komoot route (Ringelspitzhuette<->Calandahuette, 850m/760m asc/desc):
# interval=100/threshold=10 overestimated by ~250m; interval=200/threshold=25 gets within ~50m.
ELEVATION_SAMPLE_INTERVAL_M = 200
# ignore elevation swings smaller than this (meters) before counting them as real gain/loss --
# SRTM has several meters of vertical noise per sample, which otherwise inflates cumulative
# ascent/descent far above the true value (same "hysteresis" technique GPS/hiking tools use)
ELEVATION_NOISE_THRESHOLD_M = 25


def download_osm_extract(url: str = OSM_EXTRACT_URL, out_path: str = OSM_EXTRACT_PATH) -> str:
    """Download the OSM extract if it is not already cached on disk, resuming partial downloads."""
    tmp_path = out_path + ".part"
    if os.path.exists(out_path):
        print(f"Using cached OSM extract at {out_path}")
        return out_path

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    resume_from = os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0
    headers = {"Range": f"bytes={resume_from}-"} if resume_from else {}

    print(f"Downloading {url} -> {out_path} (this is a few GB, may take a while)")
    # read timeout guards against a silently stalled connection (e.g. dropped VPN)
    with requests.get(url, stream=True, timeout=(10, 30), headers=headers) as response:
        response.raise_for_status()
        mode = "ab" if resume_from and response.status_code == 206 else "wb"
        if mode == "wb":
            resume_from = 0
        downloaded = resume_from
        with open(tmp_path, mode) as out_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                out_file.write(chunk)
                downloaded += len(chunk)
                print(f"\r{downloaded / 1e6:.0f} MB downloaded", end="", flush=True)
    print()
    os.rename(tmp_path, out_path)
    return out_path


def filter_to_hiking_ways(pbf_path: str, out_path: str = HIKING_WAYS_PATH) -> str:
    """Pre-filter the (large) OSM extract down to trail-like ways using osmium-tool.

    pyrosm's default "walking" network also includes every residential/service street in
    every alpine town, which is both semantically wrong for hiking routing and far too large
    memory-wise to parse for a region the size of the whole Alps. Filtering with osmium first
    (requires the `osmium` CLI, e.g. `brew install osmium-tool`) shrinks the file substantially
    before pyrosm ever has to load it.
    """
    if os.path.exists(out_path):
        print(f"Using cached hiking-ways extract at {out_path}")
        return out_path

    tag_filter = "w/highway=" + ",".join(HIKING_HIGHWAY_TAGS)
    subprocess.run(
        ["osmium", "tags-filter", pbf_path, tag_filter, "-o", out_path], check=True
    )
    return out_path


def build_walking_graph(pbf_path: str):
    """Parse the (already trail-filtered) network from the OSM extract into an igraph graph.

    Cached on disk (graph + node coordinates) since building it from the PBF takes several
    minutes and this script is often re-run while tuning the distance-computation logic below.
    """
    if os.path.exists(GRAPH_CACHE_PATH) and os.path.exists(GRAPH_NODES_CACHE_PATH):
        print(f"Using cached graph at {GRAPH_CACHE_PATH}")
        graph = igraph.Graph.Read_Pickle(GRAPH_CACHE_PATH)
        graph_nodes = pd.read_csv(GRAPH_NODES_CACHE_PATH)
        return graph, graph_nodes

    osm = OSM(pbf_path)
    nodes, edges = osm.get_network(nodes=True, network_type="walking")
    # drop attribute columns we don't need to keep memory footprint down (geometry must be kept
    # so nodes/edges remain valid GeoDataFrames, as required by to_graph)
    nodes = nodes[["id", "lat", "lon", "geometry"]].copy()
    edges = edges[["id", "u", "v", "length", "geometry"]].copy()
    graph = osm.to_graph(nodes, edges, graph_type="igraph", network_type="walking")
    # after export, node ordering can differ from `nodes`; graph.vs carries the authoritative set
    graph_nodes = pd.DataFrame(
        {"id": graph.vs["id"], "lat": graph.vs["lat"], "lon": graph.vs["lon"]}
    )

    graph.write_pickle(GRAPH_CACHE_PATH)
    graph_nodes.to_csv(GRAPH_NODES_CACHE_PATH, index=False)
    return graph, graph_nodes


def snap_huts_to_network(huts: gpd.GeoDataFrame, graph_nodes: pd.DataFrame) -> pd.DataFrame:
    """Find the nearest walking-network node for each hut.

    Returns:
        DataFrame indexed by hut id with columns node_index (position in graph), snap_distance_m
    """
    node_coords_rad = np.radians(graph_nodes[["lat", "lon"]].to_numpy())
    tree = BallTree(node_coords_rad, metric="haversine")

    huts_with_coords = huts.dropna(subset=["latitude", "longitude"])
    query_coords_rad = np.radians(huts_with_coords[["latitude", "longitude"]].to_numpy())
    distances_rad, node_indices = tree.query(query_coords_rad, k=1)

    return pd.DataFrame(
        {
            "node_index": node_indices[:, 0],
            "snap_distance_m": distances_rad[:, 0] * EARTH_RADIUS_M,
        },
        index=huts_with_coords["id"],
    )


def _haversine_m(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Vectorized haversine distance in meters."""
    lat1, lon1, lat2, lon2 = (np.radians(a) for a in (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def compute_beeline_pairs(huts: gpd.GeoDataFrame, max_distance: float = MAX_BEELINE_DISTANCE_M) -> pd.DataFrame:
    """All ordered hut pairs within max_distance (haversine meters) of each other."""
    huts = huts.dropna(subset=["latitude", "longitude"])
    lat, lon, ids = huts["latitude"].to_numpy(), huts["longitude"].to_numpy(), huts["id"].to_numpy()
    dist = _haversine_m(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    src, tgt = np.nonzero((dist <= max_distance) & (dist > 0))
    return pd.DataFrame(
        {"id_source": ids[src], "id_target": ids[tgt], "beeline_distance_m": dist[src, tgt].astype(int)}
    )


def _cumulative_ascent_descent(elevations: list[float], threshold: float) -> tuple[float, float]:
    """Sum ascent/descent with a noise threshold (hysteresis), ignoring swings smaller than it.

    Naively summing every up/down between noisy DEM samples hugely overcounts cumulative gain;
    this only counts a climb/descent once it has moved `threshold` meters away from the last
    local extreme, same technique GPS/hiking tools use for SRTM-derived elevation profiles.
    """
    ascent, descent = 0.0, 0.0
    reference = elevations[0]
    for elevation in elevations[1:]:
        diff = elevation - reference
        if diff >= threshold:
            ascent += diff
            reference = elevation
        elif diff <= -threshold:
            descent += -diff
            reference = elevation
    return ascent, descent


def compute_elevation_profile(
    path_vertices: list[int], node_lat: np.ndarray, node_lon: np.ndarray, elevation_data
) -> tuple[float, float]:
    """Compute cumulative ascent/descent (meters) along a path using SRTM elevation data."""
    lat, lon = node_lat[path_vertices], node_lon[path_vertices]
    if len(lat) < 2:
        return 0.0, 0.0

    seg_dist = _haversine_m(lat[:-1], lon[:-1], lat[1:], lon[1:])
    cum_dist = np.concatenate([[0.0], np.cumsum(seg_dist)])
    total_dist = cum_dist[-1]
    if total_dist == 0:
        return 0.0, 0.0

    n_samples = max(2, int(total_dist // ELEVATION_SAMPLE_INTERVAL_M) + 1)
    sample_dists = np.linspace(0, total_dist, n_samples)
    sample_lat = np.interp(sample_dists, cum_dist, lat)
    sample_lon = np.interp(sample_dists, cum_dist, lon)

    elevations = [elevation_data.get_elevation(float(la), float(lo)) for la, lo in zip(sample_lat, sample_lon)]
    elevations = [e for e in elevations if e is not None]
    if len(elevations) < 2:
        return 0.0, 0.0

    return _cumulative_ascent_descent(elevations, ELEVATION_NOISE_THRESHOLD_M)


def compute_hiking_distances(
    feasible_connections: pd.DataFrame,
    hut_to_node: pd.DataFrame,
    graph,
    graph_nodes: pd.DataFrame,
    elevation_data,
) -> pd.DataFrame:
    """Compute network-based hiking distance and elevation gain/loss for every feasible pair.

    Groups targets by source hut so we only run one Dijkstra search per distinct source node.
    """
    results = []
    valid_hut_ids = set(hut_to_node.index)
    node_lat = graph_nodes["lat"].to_numpy()
    node_lon = graph_nodes["lon"].to_numpy()

    for source_id, targets in feasible_connections.groupby("id_source"):
        target_ids = [t for t in targets["id_target"] if t in valid_hut_ids]
        if source_id not in valid_hut_ids or not target_ids:
            continue
        beeline_by_target = dict(zip(targets["id_target"], targets["beeline_distance_m"]))

        source_node = int(hut_to_node.loc[source_id, "node_index"])
        source_snap = hut_to_node.loc[source_id, "snap_distance_m"]
        if source_snap > MAX_SNAP_DISTANCE_M:
            continue

        # igraph's distances() rejects duplicate target vertices (e.g. two huts snapping to the
        # same nearest node), so dedupe and look results back up per node index
        target_nodes = [int(n) for n in hut_to_node.loc[target_ids, "node_index"]]
        unique_target_nodes = sorted(set(target_nodes))
        path_lengths = graph.distances(source=source_node, target=unique_target_nodes, weights="length")[0]
        dist_by_node = dict(zip(unique_target_nodes, path_lengths))

        # filter to viable targets (distance/detour checks) before the expensive path + elevation
        # lookups below
        viable_targets = []
        for target_id in target_ids:
            target_snap = hut_to_node.loc[target_id, "snap_distance_m"]
            node_dist = dist_by_node[int(hut_to_node.loc[target_id, "node_index"])]
            if target_snap > MAX_SNAP_DISTANCE_M or not np.isfinite(node_dist):
                continue
            hiking_distance = node_dist + source_snap + target_snap
            detour_cap = max(MAX_DETOUR_RATIO * beeline_by_target[target_id], MAX_DETOUR_FLOOR_M)
            if hiking_distance > detour_cap:
                continue
            viable_targets.append((target_id, hiking_distance))
        if not viable_targets:
            continue

        viable_target_nodes = sorted({int(hut_to_node.loc[t, "node_index"]) for t, _ in viable_targets})
        paths = graph.get_shortest_paths(source_node, to=viable_target_nodes, weights="length", output="vpath")
        path_by_node = dict(zip(viable_target_nodes, paths))

        for target_id, hiking_distance in viable_targets:
            target_node = int(hut_to_node.loc[target_id, "node_index"])
            ascent_m, descent_m = compute_elevation_profile(
                path_by_node[target_node], node_lat, node_lon, elevation_data
            )
            results.append(
                {
                    "id_source": source_id,
                    "id_target": target_id,
                    "hiking_distance_m": int(hiking_distance),
                    "ascent_m": int(round(ascent_m)),
                    "descent_m": int(round(descent_m)),
                }
            )

    return pd.DataFrame(results)


def main():
    """Compute and save hiking-trail distances for all feasible hut pairs."""
    huts = gpd.read_file(os.path.join(DATA_PATH, "huts_database.geojson"))
    feasible_connections = compute_beeline_pairs(huts)

    pbf_path = download_osm_extract()
    hiking_ways_path = filter_to_hiking_ways(pbf_path)
    print("Building walking network graph (this can take a few minutes)...")
    graph, graph_nodes = build_walking_graph(hiking_ways_path)
    print(f"Graph has {graph.vcount()} nodes and {graph.ecount()} edges")

    hut_to_node = snap_huts_to_network(huts, graph_nodes)
    elevation_data = srtm.get_data()

    print(f"Computing hiking distances for {len(feasible_connections)} feasible pairs...")
    hiking_distances = compute_hiking_distances(feasible_connections, hut_to_node, graph, graph_nodes, elevation_data)

    # pairs with no viable trail route keep empty hiking columns rather than a beeline fallback
    merged = feasible_connections.merge(hiking_distances, on=["id_source", "id_target"], how="left")
    hiking_cols = ["hiking_distance_m", "ascent_m", "descent_m"]
    merged[hiking_cols] = merged[hiking_cols].astype("Int64")
    print(f"Resolved {merged['hiking_distance_m'].notna().sum()} / {len(merged)} pairs with a viable trail route")

    out_path = os.path.join(DATA_PATH, "hiking_distances.csv")
    merged.to_csv(out_path, index=False)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
