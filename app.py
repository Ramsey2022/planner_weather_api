from flask import Flask, render_template, request, abort, Response, jsonify
from dotenv import load_dotenv
import json
import urllib
import os

load_dotenv(".env")

app = Flask(__name__)


@app.route("/")
def root():
    return {"message": "Server is running."}


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200


@app.route("/forecast", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    state = request.args.get("state")

    if city is None:
        abort(400, "Missing city argument")

    if state is None:
        abort(400, "Missing state argument")

    data = {}
    data["q"] = request.args.get("city", "state")
    data["appid"] = os.getenv("WEATHER_API_KEY")
    data["units"] = "imperial"

    url_values = urllib.parse.urlencode(data)
    url = "https://api.openweathermap.org/data/2.5/forecast"
    full_url = url + "?" + url_values
    data = urllib.request.urlopen(full_url)

    resp = Response(data)
    resp.status_code = 200
    return render_template(
        "index.html",
        title="Weather Forecast",
        data=json.loads(data.read().decode("utf8")),
    )


if __name__ == "__main__":
    print("weather-api")
    app.run(host="0.0.0.0", port=80, debug=True, use_reloader=True)
