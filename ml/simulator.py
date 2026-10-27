import requests
import random
import time

API_URL = "http://localhost:5000/api/data"

def generate_reading():
    hour = time.localtime().tm_hour

    base_temp = 28 + 5 * (1 if 12 <= hour <= 16 else 0)
    temp = round(base_temp + random.uniform(-2, 2), 1)
    hum = round(random.uniform(40, 80), 1)

    if 7 <= hour <= 10 or 17 <= hour <= 20:
        aqi = random.randint(100, 200)
    else:
        aqi = random.randint(40, 120)

    return {"temp": temp, "hum": hum, "aqi": aqi}


print("🌡️  Simulator running... Press Ctrl+C to stop.\n")

while True:
    try:
        data = generate_reading()
        r = requests.post(API_URL, json=data, timeout=10)
        result = r.json()
        pred = result.get('prediction', '?')
        conf = result.get('confidence', 0) * 100
        print(f"✅ {data['temp']}°C | {data['hum']}% | AQI {data['aqi']} → {pred} ({conf:.0f}%)")
    except Exception as e:
        print(f"❌ Error: {e}")
    time.sleep(5)