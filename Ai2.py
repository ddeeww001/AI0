import requests
import datetime
import matplotlib.pyplot as plt

API_KEY = 'YOUR_API_KEY'

def get_location_input(prompt):
    return input(prompt)

def get_date_input(prompt):
    while True:
        date_str = input(prompt)
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date
        except ValueError:
            print("กรุณาใส่วันที่ในรูปแบบ YYYY-MM-DD")

def get_travel_time(origin, destination, dt):
    timestamp = int(dt.timestamp())
    url = (
        f'https://maps.googleapis.com/maps/api/directions/json?'
        f'origin={origin}&destination={destination}&departure_time={timestamp}&key={API_KEY}'
    )
    response = requests.get(url)
    data = response.json()
    try:
        duration = data['routes'][0]['legs'][0]['duration_in_traffic']['value']  # วินาที
        return duration / 60  # นาที
    except Exception:
        return None

# รับข้อมูลจากผู้ใช้
origin = get_location_input("กรุณาใส่ตำแหน่งเริ่มต้น (lat,lng หรือชื่อสถานที่): ")
destination = get_location_input("กรุณาใส่จุดหมายปลายทาง (lat,lng หรือชื่อสถานที่): ")
date = get_date_input("กรุณาใส่วันที่เดินทาง (YYYY-MM-DD): ")

# ดึงข้อมูล 24 ชั่วโมงของวันที่เลือก
traffic_data = []
for hour in range(24):
    dt = date.replace(hour=hour, minute=0, second=0, microsecond=0)
    travel_time = get_travel_time(origin, destination, dt)
    traffic_data.append(travel_time if travel_time else 0)

# คำนวณค่าเฉลี่ย
average_per_hour = sum(traffic_data) / len(traffic_data)

# หาช่วงเวลาที่รถติด (มากกว่าค่าเฉลี่ย 20%)
congestion_threshold = average_per_hour * 1.2
congested_hours = [i for i, t in enumerate(traffic_data) if t > congestion_threshold]

# คำนวณเปอร์เซ็นต์แต่ละชั่วโมง
total_traffic = sum(traffic_data)
percent_per_hour = [(t / total_traffic) * 100 if total_traffic else 0 for t in traffic_data]

# แสดงผล
print("ค่าเฉลี่ยเวลาเดินทางต่อชั่วโมง (นาที):", average_per_hour)
print("ช่วงเวลาที่รถติด (ชั่วโมง):", congested_hours)
print("เปอร์เซ็นต์แต่ละชั่วโมง:", percent_per_hour)

# วาดกราฟ
hours = [f"{i}:00" for i in range(24)]
plt.figure(figsize=(12,6))
plt.bar(hours, percent_per_hour, color=['red' if i in congested_hours else 'green' for i in range(24)])
plt.xlabel('ชั่วโมง')
plt.ylabel('เปอร์เซ็นต์เวลาเดินทาง (%)')
plt.title('เปอร์เซ็นต์เวลาเดินทางต่อชั่วโมง (รายวัน)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()