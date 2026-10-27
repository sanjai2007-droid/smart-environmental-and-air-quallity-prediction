import csv
import io
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
from database import save_reading, get_latest, get_history as db_history, get_readings_since
from predictor import predict
from genai import generate_explanation
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, '..', 'frontend'))
CORS(app)


@app.route('/')
def home():
    return render_template('dashboard.html')


@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        temp = float(data['temp'])
        hum = float(data['hum'])
        aqi = float(data['aqi'])

        label, confidence = predict(temp, hum, aqi)
        explanation = generate_explanation(temp, hum, aqi, label)

        save_reading(temp, hum, aqi, label, confidence, explanation)
        print(f"✅ {label} ({confidence*100:.1f}%) | {temp}°C {hum}% AQI={aqi}")

        return jsonify({
            "status": "ok",
            "prediction": label,
            "confidence": confidence,
            "explanation": explanation
        }), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/latest', methods=['GET'])
def latest():
    rows = get_latest(1)
    if not rows:
        return jsonify({"message": "No data yet"}), 404
    r = rows[0]
    return jsonify({
        "temp": r.temp, "hum": r.hum, "aqi": r.aqi,
        "prediction": r.prediction,
        "confidence": r.confidence,
        "explanation": r.explanation,
        "timestamp": r.timestamp.isoformat()
    })


@app.route('/api/history', methods=['GET'])
def history():
    rows = db_history(50)
    return jsonify([{
        "temp": r.temp, "hum": r.hum, "aqi": r.aqi,
        "timestamp": r.timestamp.isoformat()
    } for r in rows])


@app.route('/api/report/weekly', methods=['GET'])
def weekly_report():
    since = datetime.utcnow() - timedelta(days=7)
    rows = get_readings_since(since)
    if not rows:
        return jsonify({"period_start": since.isoformat(), "period_end": datetime.utcnow().isoformat(),
                        "count": 0, "daily": [], "readings": []})

    daily_groups = {}
    for reading in rows:
        daily_groups.setdefault(reading.timestamp.date(), []).append(reading)

    daily = [{
        "date": day.isoformat(),
        "temp": round(sum(row.temp for row in samples) / len(samples), 1),
        "hum": round(sum(row.hum for row in samples) / len(samples), 1),
        "aqi": round(sum(row.aqi for row in samples) / len(samples), 1),
        "count": len(samples)
    } for day, samples in sorted(daily_groups.items())]

    risky_count = sum(row.prediction in ("Unhealthy", "Hazardous") for row in rows)
    peak = max(rows, key=lambda row: row.aqi)
    average_aqi = sum(row.aqi for row in rows) / len(rows)
    if any(row.prediction == "Hazardous" for row in rows):
        insight = "Hazardous air-quality readings were recorded this week. Check local advisories before spending extended time outdoors."
    elif average_aqi > 100:
        insight = "Average AQI was elevated this week. Consider reducing strenuous outdoor activity when readings rise."
    else:
        insight = "Average AQI stayed at or below 100 this week. Continue monitoring daily changes."

    return jsonify({
        "period_start": since.isoformat(),
        "period_end": datetime.utcnow().isoformat(),
        "count": len(rows),
        "average_temp": round(sum(row.temp for row in rows) / len(rows), 1),
        "average_humidity": round(sum(row.hum for row in rows) / len(rows), 1),
        "average_aqi": round(average_aqi, 1),
        "peak_aqi": round(peak.aqi, 1),
        "peak_timestamp": peak.timestamp.isoformat(),
        "risky_percent": round(risky_count / len(rows) * 100),
        "daily": daily,
        "insight": insight
    })


@app.route('/api/report/weekly.csv', methods=['GET'])
def download_weekly_report():
    since = datetime.utcnow() - timedelta(days=7)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp (UTC)", "Temperature (C)", "Humidity (%)", "AQI", "Condition"])
    for row in get_readings_since(since):
        writer.writerow([row.timestamp.isoformat(), row.temp, row.hum, row.aqi, row.prediction or ""])
    return Response(output.getvalue(), mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=weekly-environment-report.csv"
    })


if __name__ == '__main__':
    print("🌍 Server starting → http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)