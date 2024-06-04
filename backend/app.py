import flask

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app, origins=["*", "null"])  # allowing any origin as well as localhost (null)


@app.route("/compute_route", methods=["GET"])
def compute_route():
    # get start latitude
    start_lat = float(request.args.get("start_lat", 1))
    # get start longitude
    start_lon = float(request.args.get("start_lon", 2))
    print("Start coordinates:", start_lat, start_lon)
    return jsonify("dummy method cannot do anything yet")


if __name__ == "__main__":
    # run
    app.run(debug=True, host="localhost", port=8989)
