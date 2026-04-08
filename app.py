from flask import Flask, render_template_string
import requests
import feedparser

app = Flask(__name__)

def get_icon(code):
    if code == 0:
        return "☀️"
    elif code in [1, 2, 3]:
        return "⛅"
    elif code in [45, 48]:
        return "🌫️"
    elif code in [51, 53, 55, 61, 63, 65]:
        return "🌧️"
    elif code in [71, 73, 75]:
        return "❄️"
    elif code in [95, 96, 99]:
        return "⛈️"
    return "🌡️"


@app.route("/")
def home():

    # 🌧️ Radar
    try:
        url = "https://api.rainviewer.com/public/weather-maps.json"
        data = requests.get(url, timeout=10).json()
        radar = data["radar"]["past"][-1]["path"]
        radar_url = f"https://tilecache.rainviewer.com{radar}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
    except:
        radar_url = ""

    # 🌡️ Clima
    try:
        weather_api = "https://api.open-meteo.com/v1/forecast?latitude=-23.42&longitude=-51.42&current_weather=true"
        r = requests.get(weather_api, timeout=10)

        if r.status_code == 200:
            w = r.json()
            c = w.get("current_weather", {})
            temp = c.get("temperature", "--")
            wind = c.get("windspeed", "--")
            code = c.get("weathercode", 0)
            icon = get_icon(code)
        else:
            temp, wind, icon = "--", "--", "🌡️"

    except:
        temp, wind, icon = "--", "--", "🌡️"

    # 📰 Notícias
    try:
        rss = "https://news.google.com/rss/search?q=meteorologia+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(rss)

        news = []
        for e in feed.entries[:5]:
            news.append(f"<a href='{e.link}' target='_blank'>{e.title}</a>")

        news_html = "<br><br>".join(news)
    except:
        news_html = "Erro ao carregar"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radar do Pedro</title>

        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

        <style>
            body {{
                margin: 0;
                font-family: Arial;
                display: flex;
                background: #0f172a;
                color: white;
                transition: 0.3s;
            }}

            body.mobile {{
                flex-direction: column;
            }}

            #sidebar {{
                width: 300px;
                background: #111827;
                padding: 15px;
            }}

            body.mobile #sidebar {{
                width: 100%;
                height: 40%;
            }}

            #map {{
                flex: 1;
                height: 100vh;
            }}

            body.mobile #map {{
                height: 60vh;
            }}

            .card {{
                background: #1f2937;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
            }}

            button {{
                padding: 10px;
                border: none;
                border-radius: 8px;
                background: #2563eb;
                color: white;
                cursor: pointer;
                margin-bottom: 10px;
            }}
        </style>
    </head>

    <body>

        <div id="sidebar">
            <button onclick="toggleMobile()">📱 Modo Mobile</button>

            <h2>🌍 Radar</h2>

            <div class="card">
                <b>Clima</b><br><br>
                {icon} {temp}°C<br>
                🌬️ {wind} km/h
            </div>

            <div class="card">
                <b>📰 Notícias</b><br><br>
                {news_html}
            </div>
        </div>

        <div id="map"></div>

        <script>
            function toggleMobile() {{
                document.body.classList.toggle("mobile");
            }}

            var map = L.map('map').setView([-23.42, -51.42], 6);

            var base = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);

            {"L.tileLayer('" + radar_url + "', {opacity: 0.6}).addTo(map);" if radar_url else ""}

            map.setMinZoom(5);
            map.setMaxZoom(14);
        </script>

    </body>
    </html>
    """

    return render_template_string(html)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)