# Public Transport Airbnb

## Installation:

Download repo and install all dependencies into a conda environment with the following:

```
git clone https://github.com/NinaWie/public_transport_airbnb
cd public_transport_airbnb
conda create -n airbnb_env
conda activate airbnb_env
cd backend
pip install -e .
```

or simply build with Docker

```
docker build -t public_transport_airbnb .
```

## Development

* work on `develop` branch by default
* use [conventional commit style for automatic semantic versioning and releases](https://engineering.deloitte.com.au/articles/semantic-versioning-with-conventional-commits) via CI
* install [pre-commit](https://pre-commit.com/) hook: `pre-commit install` to force correctness before every commit

### Docker

```
docker build -t public_transport_airbnb .
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
* Find out how to download airbnb locations -> see [notebook](backend/airbnb_project.ipynb)
* Set up basic web app with map
