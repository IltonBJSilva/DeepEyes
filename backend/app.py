from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from .models import db, Annotation, SatelliteImage
from geoalchemy2 import Geometry
from sqlalchemy import text
import base64
import requests
from datetime import datetime
import json
import redis


# ----- CONFIGURAÇÃO -----
SQLALCHEMY_DATABASE_URI = (
    "postgresql://neondb_owner:npg_iXUr9zeV1xEa@ep-weathered-fog-acqya7nv-pooler.sa-east-1.aws.neon.tech/neondb"
    "?sslmode=require&channel_binding=require"
)
SECRET_KEY = "teste123"
NASA_API_KEY = "2lKrd3NQRCRAadHid5sSA7k0P0pZW5uwr4Lca7BU"  # Substitua pelo seu API Key real

# URL do Redis remoto (a que você pegou do site)
REDIS_URL = "redis://default:OFYDnlCkLdDclP5ISQfHY8v974FK23m4@redis-18735.c336.samerica-east1-1.gce.redns.redis-cloud.com:18735"

# Conexão
r = redis.Redis.from_url(REDIS_URL)


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

# ----- DB -----
db.init_app(app)
with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    db.create_all()




def get_cached_image(key):
    """Pega imagem do Redis pelo cache"""
    cached = r.get(key)
    if cached:
        return cached
    return None

def set_cached_image(key, img_bytes, expire=3600):
    """Salva imagem no Redis com tempo de expiração em segundos (padrão: 1h)"""
    r.set(key, img_bytes, ex=expire)



@app.route("/api/redis-test")
def redis_test():
    try:
        # Testa se o Redis responde
        if r.ping():
            # Testa salvar e ler um valor
            r.set("flask_test", "ok", ex=10)  # expira em 10 segundos
            value = r.get("flask_test")
            return jsonify({"status": "Redis funcionando ✅", "valor_teste": value.decode("utf-8")})
        else:
            return jsonify({"status": "Redis não respondeu ❌"})
    except Exception as e:
        return jsonify({"status": "Erro ao conectar Redis ❌", "erro": str(e)})




# =========================================================
# 🔹 FUNÇÕES AUXILIARES
# =========================================================
def image_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode("utf-8")





# =========================================================
# 🔹 FUNÇÃO DE BUSCA NASA
# =========================================================
def search_in_embeddings(query, max_results=5):
    """
    Busca imagens reais na NASA Image and Video Library ou APOD,
    filtrando concept art, IA e imagens de divulgação.
    """
    query_lower = query.lower()
    results = []

    try:
        if query_lower == "apod":
            url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&count={max_results}"
            resp = requests.get(url, timeout=10).json()
            for i, item in enumerate(resp):
                results.append({
                    "id": i+1,
                    "text": item.get("title", "Sem título"),
                    "image_url": item.get("url")
                })
        else:
            url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"
            resp = requests.get(url, timeout=10).json()
            items = resp.get("collection", {}).get("items", [])

            forbidden_keywords = ["concept", "artist", "illustration", "ia", "render", "simulation", "mockup"]

            for item in items:
                data = item.get("data", [{}])[0]
                title = data.get("title", "Sem título")
                description = data.get("description", "").lower()

                # Filtra concept art / IA
                if any(word in title.lower() for word in forbidden_keywords):
                    continue
                if any(word in description for word in forbidden_keywords):
                    continue

                # Pega o link da imagem
                links = item.get("links", [{}])
                image_url = None
                for link in links:
                    if link.get("render") == "image" and link.get("href"):
                        image_url = link.get("href")
                        break
                if not image_url:
                    continue

                results.append({
                    "id": len(results)+1,
                    "text": title,
                    "image_url": image_url
                })

                if len(results) >= max_results:
                    break

        if not results:
            results.append({
                "id": 1,
                "text": f"Nenhuma imagem real encontrada para '{query}'",
                "image_url": None
            })

    except Exception as e:
        results.append({
            "id": 1,
            "text": f"Erro ao buscar imagens NASA: {str(e)}",
            "image_url": None
        })

    return results


# =========================================================
# 🔹 FRONTEND
# =========================================================
@app.route("/")
def home():
    return render_template("index2.html")

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
    results = search_in_embeddings(query, max_results=10)
    return jsonify({"results": results})


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


@app.route("/api/images", methods=["GET", "POST"])
def images_route():
    if request.method == "GET":
        images_list = []
        for img in SatelliteImage.query.all():
            cache_key = f"image:{img.id}"
            cached = get_cached_image(cache_key)  # Presume que você tem essa função
            if cached:
                img_base64 = image_to_base64(cached)
                cached_flag = True
            elif img.url:
                response = requests.get(img.url)
                img_bytes = response.content
                set_cached_image(cache_key, img_bytes)  # Presume que você tem essa função
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
            url=data.get("url")
        )
        db.session.add(new_image)
        db.session.commit()
        return jsonify({"status": "image added"})


# =========================================================
# 🔹 FRONTEND
# =========================================================
@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# 🔹 HEALTH CHECK
# =========================================================
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Flask API DeepEyes UP!"})


# =========================================================
# 🔹 API NASA DIVERSOS
# =========================================================
@app.route("/api/nasa/<string:dataset>", methods=["GET"])
def fetch_nasa_data(dataset):
    cache_key = f"nasa:{dataset}"
    cached = get_cached_image(cache_key)  # Presume função de cache
    if cached:
        return jsonify(eval(cached.decode("utf-8")))

    if dataset == "worldview":
        url = "https://worldview.earthdata.nasa.gov/"
        result = {"info": "Exploração visual da Terra (Worldview)", "url": url}

    elif dataset == "mars":
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={NASA_API_KEY}"
        resp = requests.get(url).json()
        result = {"dataset": "Mars Reconnaissance Orbiter", "photos": resp.get("photos", [])[:5]}

    elif dataset == "tess":
        url = "https://tess.mit.edu/data/"
        result = {"dataset": "TESS", "info": "Informações sobre o satélite TESS", "url": url}

    elif dataset == "lunar":
        url = "https://lunar.gsfc.nasa.gov/"
        result = {"dataset": "Lunar Reconnaissance Orbiter", "url": url}

    elif dataset == "solar_system_treks":
        url = "https://trek.nasa.gov/"
        result = {"dataset": "Solar System Treks", "url": url}

    elif dataset == "earthdata":
        url = "https://earthdata.nasa.gov/"
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
