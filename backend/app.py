from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from .models import db, Annotation, SatelliteImage
from geoalchemy2 import Geometry
from sqlalchemy import text

# ----- CONFIGURAÇÃO COM NEON ----- 
SQLALCHEMY_DATABASE_URI = (
    "postgresql://neondb_owner:npg_iXUr9zeV1xEa@ep-weathered-fog-acqya7nv-pooler.sa-east-1.aws.neon.tech/neondb"
    "?sslmode=require&channel_binding=require"
)
SECRET_KEY = "teste123"

# ----- APP FLASK -----
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ----- CORS -----
CORS(app)

# ----- INICIALIZAÇÃO DO DB -----
db.init_app(app)

with app.app_context():
    # Cria extensão PostGIS se ainda não existir
    with db.engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

    db.create_all()

# ----- FUNÇÃO SIMULADA DE BUSCA -----
def search_in_embeddings(query):
    return [{"id": 1, "text": f"Resultado simulado para '{query}'"}]

# ----- ROTAS FRONTEND -----
@app.route("/")
def home():
    return render_template("index.html")

# ----- ROTAS API -----
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Flask API DeepEyes UP!"})

@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    results = search_in_embeddings(query)
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
        images = SatelliteImage.query.all()
        return jsonify([{
            "id": i.id,
            "description": i.description,
            "location": str(i.location),
            "timestamp": i.timestamp,
            "source": i.source
        } for i in images])

    elif request.method == "POST":
        data = request.get_json()
        new_image = SatelliteImage(
            description=data.get("description"),
            location=f"POINT({data['lon']} {data['lat']})",
            timestamp=data.get("timestamp"),
            source=data.get("source")
        )
        db.session.add(new_image)
        db.session.commit()
        return jsonify({"status": "image added"})

# ----- RODAR LOCAL -----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
