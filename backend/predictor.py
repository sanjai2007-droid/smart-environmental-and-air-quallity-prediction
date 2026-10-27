import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, '..', 'models')

model = None
scaler = None
labels = None


def load_artifacts():
    """Lazy load - model file irundha load pannum."""
    global model, scaler, labels
    if model is not None:
        return True

    model_path = os.path.join(MODEL_DIR, 'air_quality_dnn.h5')
    scaler_path = os.path.join(MODEL_DIR, 'scaler.pkl')
    labels_path = os.path.join(MODEL_DIR, 'labels.pkl')
    if not all(os.path.exists(path) for path in (model_path, scaler_path, labels_path)):
        return False

    import pickle
    import numpy as np
    from tensorflow.keras.models import load_model

    model = load_model(model_path)
    with open(scaler_path, 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    with open(labels_path, 'rb') as labels_file:
        labels = pickle.load(labels_file)
    return True


def predict(temp, hum, aqi, hour=None):
    """Predict AQI class. Model illama na rule-based fallback."""
    if hour is None:
        hour = datetime.now().hour

    if not load_artifacts():
        # Fallback rule-based
        if aqi <= 50:
            return "Good", 0.9
        elif aqi <= 100:
            return "Moderate", 0.8
        elif aqi <= 200:
            return "Unhealthy", 0.85
        else:
            return "Hazardous", 0.9

    X = scaler.transform([[temp, hum, aqi, hour]])
    probs = model.predict(X, verbose=0)[0]
    idx = int(np.argmax(probs))
    return labels[idx], float(probs[idx])