from flask import Flask, request, Response, jsonify
from dotenv import load_dotenv
from datetime import datetime
import json
import urllib
import os
import googlemaps

load_dotenv(".env")
API_KEY = os.getenv("google_map_key")

app = Flask(__name__)


@app.route("/")
def root():
    return {"message": "Server is running."}


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200


@app.route("/forecast", methods=["GET", "POST"])
def get_weather():
    json_data = request.get_json()

    # googlemaps geocoder for lat/lon + current date
    gmaps = googlemaps.Client(key=API_KEY)
    geocode_results = gmaps.geocode(json_data["postal_code"])
    lats = geocode_results[0]["geometry"]["location"]["lat"]
    lons = geocode_results[0]["geometry"]["location"]["lng"]
    datenow = datetime.now().date()

    # data params for weather api url
    data = {}
    data["lat"] = lats
    data["lon"] = lons
    data["date"] = datenow
    data["appid"] = os.getenv("WEATHER_API_KEY")
    data["units"] = "imperial"
    data["exclude"] = ("current", "minutely", "hourly", "alerts")

    url_values = urllib.parse.urlencode(data)
    url = "https://api.openweathermap.org/data/3.0/onecall"
    full_url = url + "?" + url_values
    data = urllib.request.urlopen(full_url)

    resp = Response(data)
    resp.status_code = 200

    json_data = json.loads(data.read().decode("utf8"))

    weather_data = []

    for item in json_data["daily"]:
        weather = {
            "dayname": datetime.fromtimestamp(item["dt"]).strftime("%A"),
            "date": datetime.fromtimestamp(item["dt"]).strftime("%d %B, %Y"),
            "temp_max": item["temp"]["max"],
            "temp_min": item["temp"]["min"],
            "humidity": item["humidity"],
            "wind": item["wind_speed"],
            "icon": item["weather"][0]["icon"],
            "main": item["weather"][0]["main"],
        }
        weather_data.append(weather)

    return jsonify(weather_data)


if __name__ == "__main__":
    print("weather-api")
    app.run(host="0.0.0.0", port=80, debug=True, use_reloader=True)
