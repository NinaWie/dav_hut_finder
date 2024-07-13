from flask import Flask, request, jsonify
from flask_cors import CORS

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
    print('Received data:', data)
    # Here, you can process the data as needed
    return jsonify({'status': 'success', 'data': data})




def convert_to_float(request, col_name, default):
    try:
        return float(request.args.get(col_name, default))
    except ValueError:
        return default


if __name__ == '__main__':
    app.run(debug=True)
