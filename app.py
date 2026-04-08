from flask import Flask, render_template_string
import requests
import feedparser

app = Flask(__name__)

def get_icon(code):
    if code == 0:
        return "☀️"
    elif code in [1,2,3]:
        return "⛅"
    elif code in [45,48]:
        return "🌫️"
    elif code in [51,53,55,61,63,65]:
        return "🌧️"
    elif code in [71,73,75]:
        return "❄️"
    elif code in [95,96,99]:
        return "⛈️"
    return "🌡️"


@app.route("/")
def home():

    # Radar
    try:
        data = requests.get("https://api.rainviewer.com/public/weather-maps.json", timeout=10).json()
        radar = data["radar"]["past"][-1]["path"]
        radar_url = f"https://tilecache.rainviewer.com{radar}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
    except:
        radar_url = ""

    # Clima
    try:
        w = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=-23.42&longitude=-51.42&current_weather=true",
            timeout=10
        ).json()

        c = w.get("current_weather", {})
        temp = c.get("temperature", "--")
        wind = c.get("windspeed", "--")
        icon = get_icon(c.get("weathercode", 0))
    except:
        temp, wind, icon = "--", "--", "🌡️"

    # Notícias
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=meteorologia+Brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419")
        news_html = "<br><br>".join(
            [f"<a href='{e.link}' target='_blank'>{e.title}</a>" for e in feed.entries[:5]]
        )
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
                background: #0f172a;
                color: white;
                overflow: hidden;
            }}

            #map {{
                position: absolute;
                width: 100%;
                height: 100%;
            }}

            /* Sidebar estilo app mobile */
            #sidebar {{
                position: absolute;
                top: 0;
                left: 0;
                width: 280px;
                height: 100%;
                background: #111827;
                padding: 15px;
                transform: translateX(0);
                transition: 0.3s;
                z-index: 1000;
                overflow-y: auto;
            }}

            #sidebar.hidden {{
                transform: translateX(-260px);
            }}

            /* Botão seta */
            #toggle {{
                position: absolute;
                top: 20px;
                left: 280px;
                background: #2563eb;
                padding: 10px;
                border-radius: 50%;
                cursor: pointer;
                z-index: 1100;
                transition: 0.3s;
            }}

            #toggle.hidden {{
                left: 20px;
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

            /* MOBILE REAL (9:16 vibe) */
            @media (max-width: 768px) {{
                #sidebar {{
                    width: 85%;
                }}

                #toggle {{
                    left: 85%;
                }}

                #sidebar.hidden {{
                    transform: translateX(-90%);
                }}
            }}
        </style>
    </head>

    <body>

        <div id="sidebar">
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

        <div id="toggle" onclick="toggleSidebar()">⬅️</div>

        <div id="map"></div>

        <script>
            function toggleSidebar() {{
                let sidebar = document.getElementById("sidebar");
                let toggle = document.getElementById("toggle");

                sidebar.classList.toggle("hidden");
                toggle.classList.toggle("hidden");

                toggle.innerHTML = sidebar.classList.contains("hidden") ? "➡️" : "⬅️";
            }}

            var map = L.map('map').setView([-23.42, -51.42], 6);

            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);

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