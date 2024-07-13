from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/markers')
def markers():
    markers_data = [
        {"id": 1, "name": "Marker 1", "position": [46.5, 10.5]},
        {"id": 2, "name": "Marker 2", "position": [45.8326, 6.8652]},
        {"id": 3, "name": "Marker 3", "position": [45.9763, 7.6586]},
        {"id": 4, "name": "Marker 4", "position": [47.4210, 10.9849]}
    ]
    return jsonify(markers_data)

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json

    # Convert strings to floats and date string to datetime object
    processed_data = {
        'longitude': float(data['longitude']),
        'latitude': float(data['latitude']),
        'min_distance': float(data['minDistance']),
        'max_distance': float(data['maxDistance']),
        'min_altitude': float(data['minAltitude']),
        'max_altitude': float(data['maxAltitude']),
        'date': datetime.strptime(data['date'], '%Y-%m-%d')
    }

    print('Received data:', processed_data)
    # Here, you can process the data as needed
    return jsonify({'status': 'success', 'data': processed_data})

if __name__ == '__main__':
    app.run(debug=True)
