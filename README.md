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