import os
from dotenv import load_dotenv

load_dotenv()

# Gemini try pannuvom; illama na fallback rule-based
try:
    import google.generativeai as genai
    API_KEY = os.getenv("GEMINI_API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        USE_AI = True
    else:
        USE_AI = False
except Exception:
    USE_AI = False


def _fallback(temp, hum, aqi, label):
    """Provide simple English advice when AI is unavailable."""
    advice = {
        "Good": "🌱 Air quality is good. It is safe to walk outside. You can open the windows.",
        "Moderate": "😐 Air quality is moderate. Sensitive individuals should wear a mask outdoors.",
        "Unhealthy": "⚠️ Air pollution is high. Wear a mask outdoors and use an air purifier.",
        "Hazardous": "🚨 Air quality is hazardous. Avoid going outside. Everyone should use a mask and air purifier."
    }
    return f"{advice.get(label, 'Data received.')} (Temp: {temp}°C, Hum: {hum}%, AQI: {aqi})"


def generate_explanation(temp, hum, aqi, label):
    if not USE_AI:
        return _fallback(temp, hum, aqi, label)

    prompt = f"""You are an environmental health advisor.
Sensor data:
- Temperature: {temp}°C
- Humidity: {hum}%
- AQI: {aqi}
- Predicted condition: {label}

Reply in English, EXACTLY 3 short bullet points:
• Health impact (1 line)
• 3 quick actions (comma separated)
• Who is at risk (1 line)

Under 60 words total."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return _fallback(temp, hum, aqi, label)