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

    # 🌧️ Radar (RainViewer)
    try:
        url = "https://api.rainviewer.com/public/weather-maps.json"
        data = requests.get(url, timeout=5).json()
        radar = data["radar"]["past"][-1]["path"]
        radar_url = f"https://tilecache.rainviewer.com{radar}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
    except:
        radar_url = ""

    # 🌡️ Clima atual
    try:
        weather_api = "https://api.open-meteo.com/v1/forecast?latitude=-23.42&longitude=-51.42&current_weather=true"
        w = requests.get(weather_api, timeout=5).json()

        temp = w["current_weather"]["temperature"]
        wind = w["current_weather"]["windspeed"]
        code = w["current_weather"]["weathercode"]
        icon = get_icon(code)
    except:
        temp = "--"
        wind = "--"
        code = "--"
        icon = "🌡️"

    # 📰 Notícias
    try:
        rss_url = "https://news.google.com/rss/search?q=meteorologia+chuva+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(rss_url)

        news = []
        for e in feed.entries[:5]:
            news.append(f"<a href='{e.link}' target='_blank'>{e.title}</a>")

        news_html = "<br><br>".join(news) if news else "Sem notícias"
    except:
        news_html = "Erro ao carregar notícias"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radar Meteorológico</title>

        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

        <style>
            body {{
                margin: 0;
                font-family: Arial;
                display: flex;
                background: #0f172a;
                color: white;
            }}

            #sidebar {{
                width: 300px;
                background: #111827;
                padding: 15px;
                overflow-y: auto;
            }}

            #map {{
                flex: 1;
                height: 100vh;
            }}

            .card {{
                background: #1f2937;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
            }}

            a {{
                color: #60a5fa;
                text-decoration: none;
                font-size: 13px;
            }}
        </style>
    </head>

    <body>

        <div id="sidebar">
            <h2>🌍 Radar</h2>

            <div class="card">
                <b>Clima atual</b><br><br>
                {icon} {temp}°C<br>
                🌬️ {wind} km/h<br>
                Código: {code}
            </div>

            <div class="card">
                <b>📰 Notícias</b><br><br>
                {news_html}
            </div>
        </div>

        <div id="map"></div>

        <script>
            var map = L.map('map').setView([-23.42, -51.42], 6);

            var base = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);

            {"var radar = L.tileLayer('" + radar_url + "', {opacity: 0.6}).addTo(map);" if radar_url else ""}

            map.setMinZoom(5);
            map.setMaxZoom(14);
        </script>

    </body>
    </html>
    """

    return render_template_string(html)


# 🔥 ESSENCIAL PRO RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)