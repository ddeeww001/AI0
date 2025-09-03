import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

GOOGLE_MAPS_API_KEY = 'YOUR_API_KEY'

def get_traffic_data(origin, destination, departure_time):
    url = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={origin}&destination={destination}"
        f"&departure_time={departure_time}&key={GOOGLE_MAPS_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    return data

def analyze_traffic(data):
    if 'routes' not in data or not data['routes']:
        return {"status": "error", "message": "ไม่พบเส้นทาง"}
    route = data['routes'][0]
    legs = route['legs'][0]
    duration_in_traffic = legs.get('duration_in_traffic', {}).get('text', 'ไม่ทราบข้อมูล')
    steps = [
        {
            "instruction": step['html_instructions'],
            "distance": step['distance']['text'],
            "duration": step['duration']['text'],
            "start_location": step['start_location'],
            "end_location": step['end_location']
        }
        for step in legs.get('steps', [])
    ]
    summary = {
        "distance": legs['distance']['text'],
        "duration": legs['duration']['text'],
        "duration_in_traffic": duration_in_traffic,
        "start_address": legs['start_address'],
        "end_address": legs['end_address'],
        "steps": steps,
        "overview_polyline": route.get('overview_polyline', {}).get('points', '')
    }
    return summary

def get_traffic_by_times(origin, destination):
    times = []
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    for hour in range(6, 22):  # 6:00 to 21:00
        dt = now.replace(hour=hour)
        timestamp = int(dt.timestamp())
        data = get_traffic_data(origin, destination, timestamp)
        result = analyze_traffic(data)
        times.append({
            "hour": hour,
            "duration_in_traffic": result.get("duration_in_traffic", "ไม่ทราบข้อมูล")
        })
    return times

@app.route('/check-traffic', methods=['POST'])
def check_traffic():
    try:
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        if origin and destination:
            now = int(datetime.now().timestamp())
            traffic_data = get_traffic_data(origin, destination, now)
            result = analyze_traffic(traffic_data)
            return jsonify(result)
        else:
            return jsonify({'status': 'error', 'message': 'กรุณาระบุสถานที่ต้นทางและปลายทาง'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/traffic_times', methods=['POST'])
def traffic_times():
    try:
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        if origin and destination:
            times = get_traffic_by_times(origin, destination)
            return jsonify(times)
        else:
            return jsonify({'status': 'error', 'message': 'กรุณาระบุสถานที่ต้นทางและปลายทาง'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    traffic_info = None
    traffic_times_info = None
    map_data = None
    if request.method == 'POST':
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        if origin and destination:
            now = int(datetime.now().timestamp())
            data = get_traffic_data(origin, destination, now)
            traffic_info = analyze_traffic(data)
            traffic_times_info = get_traffic_by_times(origin, destination)
            map_data = {
                "origin": origin,
                "destination": destination,
                "overview_polyline": traffic_info.get("overview_polyline", ""),
                "steps": traffic_info.get("steps", [])
            }
    return render_template('page1.html', traffic_info=traffic_info, traffic_times_info=traffic_times_info, map_data=map_data, api_key=GOOGLE_MAPS_API_KEY)

if __name__ == '__main__':
    app.run(debug=True)