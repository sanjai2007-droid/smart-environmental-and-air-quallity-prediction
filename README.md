# Smart Environmental and Air Quality Prediction

Flask-powered environmental monitoring dashboard with air-quality predictions,
sensor history, and weekly reports.

## Deploy on Render

Click the button to create a Render web service from this repository:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sanjai2007-droid/smart-environmental-and-air-quallity-prediction)

Render builds the Python dependencies and starts the Flask app with Gunicorn.
When deployment finishes, open the service's **URL** in the Render dashboard to
use the website. The Flask app serves the dashboard and API from the same URL.

`GEMINI_API_KEY` is optional. Add it under the Render service's environment
variables to enable Gemini-generated explanations; without it, the app uses its
built-in advice.

The deployed service uses the built-in AQI rule-based prediction unless trained
model artifacts are provided. The model files are excluded from this repository.

The service uses SQLite by default. Render's free service has an ephemeral
filesystem, so saved sensor readings can be lost when the service restarts.

## Send sensor readings

The dashboard displays readings submitted to the API. Send JSON to
`POST /api/data` on the deployed service:

```json
{
  "temp": 28.5,
  "hum": 60,
  "aqi": 75
}
```

For local development, install `requirements.txt` and run:

```powershell
python backend\app.py
```

Then open `http://localhost:5000`.
