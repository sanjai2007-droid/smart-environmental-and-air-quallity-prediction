import pandas as pd
import numpy as np
import pickle
import os
from tensorflow.keras import layers, models
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, '..', 'data', 'sensor_data.csv')
MODEL_DIR = os.path.join(BASE, '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

print("📂 Loading dataset...")
df = pd.read_csv(DATA_PATH)

X = df[['temp', 'hum', 'aqi', 'hour']].values
labels = ["Good", "Moderate", "Unhealthy", "Hazardous"]
y = np.array([[1 if lab == l else 0 for l in labels] for lab in df['label'].values])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)
with open(os.path.join(MODEL_DIR, 'labels.pkl'), 'wb') as f:
    pickle.dump(labels, f)

print("🧠 Building DNN...")
model = models.Sequential([
    layers.Input(shape=(4,)),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(32, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(16, activation='relu'),
    layers.Dense(4, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

print("🚀 Training...")
history = model.fit(
    X_train, y_train,
    epochs=30, batch_size=32,
    validation_split=0.2, verbose=1
)

loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"\n✅ Test Accuracy: {acc * 100:.2f}%")

model.save(os.path.join(MODEL_DIR, 'air_quality_dnn.h5'))
print(f"✅ Model saved → {MODEL_DIR}/air_quality_dnn.h5")