from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)





@app.route('/api/data')
def get_data():
    data = {
        'message': 'Hello from Flask!',
        'coordinates': [51, 7]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)
