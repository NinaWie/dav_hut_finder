# Alpenverein hut finder

Filter huts in the alps by
* distance from starting location
* Public transport accessibility
* Available places at a specific date

## Installation:

Download repo and install all dependencies into a conda environment with the following:

```
git clone https://github.com/NinaWie/dav_hut_finder
cd dav_hut_finder
conda create -n dav_env
conda activate dav_env
cd backend
pip install -e .
```

or simply build with Docker

```
docker build -t dav_hut_finder .
```

## Development

* work on `develop` branch by default
* use [conventional commit style for automatic semantic versioning and releases](https://engineering.deloitte.com.au/articles/semantic-versioning-with-conventional-commits) via CI
* install [pre-commit](https://pre-commit.com/) hook: `pre-commit install` to force correctness before every commit

### Docker

```
docker compose up
```

Open your browser at `http://localhost:8989/`

The compose file mounts the correct files so hot reloading works without re-building.

## Flask demo

Simple flask demo already works, to test it, run
```
cd backend
python app.py
```
Open the index.html (folder `frontend`) in a browser and test by inputting latitude and longitude and pressing the button.

## Next steps

* Find out how to efficiently download PT stations -> see [notebook](backend/airbnb_project.ipynb)
* Compute distance of huts from closest PT station -> best with spatial join in [geopandas](https://geopandas.org/en/stable/gallery/spatial_joins.html). The huts are already available in geojson format in our [database](backend/data/huts_database.geojson) which can be loaded via `gpd.read_file(file_path, driver="GeoJSON")`.
* Set up basic web app with map
