from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, Annotation, SatelliteImage
from geoalchemy2 import Geometry
from sqlalchemy import text
import base64
import requests
from datetime import datetime
import json

# ----- CONFIGURAÇÃO -----
SQLALCHEMY_DATABASE_URI = (
    "postgresql://neondb_owner:npg_iXUr9zeV1xEa@ep-weathered-fog-acqya7nv-pooler.sa-east-1.aws.neon.tech/neondb"
    "?sslmode=require&channel_binding=require"
)
SECRET_KEY = "teste123"
NASA_API_KEY = "2lKrd3NQRCRAadHid5sSA7k0P0pZW5uwr4Lca7BU"  # Substitua pelo seu API Key real

# ----- APP FLASK -----
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

# ----- REDIS -----
#redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=False)

# ----- DB -----
db.init_app(app)
with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    db.create_all()

# =========================================================
# 🔹 FUNÇÕES DE CACHE
# =========================================================


def image_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode("utf-8")

# =========================================================
# 🔹 FUNÇÃO SIMULADA DE BUSCA
# =========================================================
import json

def search_in_embeddings(query):
    query_lower = query.lower()
    results = []

    # Exemplo: Marte
    if "marte" in query_lower or "mars" in query_lower:
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={NASA_API_KEY}"
        try:
            resp = requests.get(url, timeout=10).json()
            photos = resp.get("photos", [])[:5]  # pegar só os 5 primeiros
            for i, photo in enumerate(photos):
                results.append({
                    "id": i+1,
                    "text": f"Foto de Marte - {photo['camera']['full_name']}",
                    "image_url": photo['img_src']
                })
        except Exception as e:
            results.append({"id": 1, "text": f"Erro ao buscar imagens de Marte: {str(e)}"})

    # Exemplo: Terra
    elif "terra" in query_lower or "earth" in query_lower:
        # Simulação usando imagens de satélite públicas (Worldview)
        results.append({
            "id": 1,
            "text": "Imagem simulada da Terra",
            "image_url": "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57730/world.topo.bathy.200412.3x5400x2700.jpg"
        })

    # Qualquer outra coisa
    else:
        results.append({
            "id": 1,
            "text": f"Resultado simulado para '{query}'",
            "image_url": None
        })

    return results


# =========================================================
# 🔹 FRONTEND
# =========================================================
@app.route("/")
def home():
    return render_template("index.html")

# =========================================================
# 🔹 API HEALTH
# =========================================================
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Flask API DeepEyes UP!"})

# =========================================================
# 🔹 API SEARCH
# =========================================================
@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    results = search_in_embeddings(query)
    return jsonify({"results": results})

# =========================================================
# 🔹 API ANNOTATIONS
# =========================================================
@app.route("/api/annotations", methods=["GET", "POST"])
def annotations_route():
    if request.method == "GET":
        annotations = Annotation.query.all()
        return jsonify([{"id": a.id, "text": a.text} for a in annotations])
    elif request.method == "POST":
        data = request.get_json()
        new_annotation = Annotation(text=data.get("text"))
        db.session.add(new_annotation)
        db.session.commit()
        return jsonify({"status": "annotation added"})

# =========================================================
# 🔹 API IMAGES (Cache + Download)
# =========================================================
@app.route("/api/images", methods=["GET", "POST"])
def images_route():
    if request.method == "GET":
        images_list = []
        for img in SatelliteImage.query.all():
            cache_key = f"image:{img.id}"
            cached = get_cached_image(cache_key)
            if cached:
                img_base64 = image_to_base64(cached)
                cached_flag = True
            elif img.url:
                response = requests.get(img.url)
                img_bytes = response.content
                set_cached_image(cache_key, img_bytes)
                img_base64 = image_to_base64(img_bytes)
                cached_flag = False
            else:
                img_base64 = None
                cached_flag = False

            images_list.append({
                "id": img.id,
                "description": img.description,
                "location": str(img.location),
                "timestamp": img.timestamp,
                "source": img.source,
                "cached": cached_flag,
                "image_base64": img_base64
            })
        return jsonify(images_list)

    elif request.method == "POST":
        data = request.get_json()
        new_image = SatelliteImage(
            description=data.get("description"),
            location=f"POINT({data['lon']} {data['lat']})",
            timestamp=datetime.strptime(data.get("timestamp"), "%Y-%m-%dT%H:%M:%S"),
            source=data.get("source"),
            url=data.get("url")  # URL da API NASA ou outro
        )
        db.session.add(new_image)
        db.session.commit()
        return jsonify({"status": "image added"})

# =========================================================
# 🔹 API NASA (puxa dados de várias fontes)
# =========================================================
@app.route("/api/nasa/<string:dataset>", methods=["GET"])
def fetch_nasa_data(dataset):
    """
    dataset pode ser:
        - worldview
        - mars
        - tess
        - lunar
        - solar_system_treks
        - earthdata
    """
    cache_key = f"nasa:{dataset}"
    cached = get_cached_image(cache_key)
    if cached:
        return jsonify(eval(cached.decode("utf-8")))

    if dataset == "worldview":
        url = ""
        result = {"info": "Exploração visual da Terra (Worldview)", "url": url}

    elif dataset == "mars":
        url = f""
        resp = requests.get(url).json()
        result = {"dataset": "Mars Reconnaissance Orbiter", "photos": resp.get("photos", [])[:5]}

    elif dataset == "tess":
        url = ""
        result = {"dataset": "TESS", "info": "Informações sobre o satélite TESS", "url": url}

    elif dataset == "lunar":
        url = ""
        result = {"dataset": "Lunar Reconnaissance Orbiter", "url": url}

    elif dataset == "solar_system_treks":
        url = ""
        result = {"dataset": "Solar System Treks", "url": url}

    elif dataset == "earthdata":
        url = ""
        result = {"dataset": "EarthData", "url": url}

    else:
        result = {"error": "Dataset não encontrado"}

    set_cached_image(cache_key, str(result).encode("utf-8"))
    return jsonify(result)

# =========================================================
# ----- RODAR LOCAL -----
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
