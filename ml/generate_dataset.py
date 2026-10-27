import pandas as pd
import random
import os

rows = []
for _ in range(5000):
    temp = round(random.uniform(20, 42), 1)
    hum = round(random.uniform(30, 90), 1)
    aqi = random.randint(20, 350)
    hour = random.randint(0, 23)

    if aqi <= 50:
        label = "Good"
    elif aqi <= 100:
        label = "Moderate"
    elif aqi <= 200:
        label = "Unhealthy"
    else:
        label = "Hazardous"

    rows.append([temp, hum, aqi, hour, label])

df = pd.DataFrame(rows, columns=['temp', 'hum', 'aqi', 'hour', 'label'])

output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sensor_data.csv')
df.to_csv(output_path, index=False)

print(f"✅ Generated {len(df)} rows → {output_path}")
print(df['label'].value_counts())