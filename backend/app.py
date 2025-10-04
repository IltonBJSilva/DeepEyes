from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, Annotation
from search_index import search_in_embeddings
from .config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
import os

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)

# ⚡ Inicializa SQLAlchemy com o app
db.init_app(app)

# ⚡ Cria tabelas dentro do contexto da app
with app.app_context():
    db.create_all()

# --- Rotas Frontend
@app.route("/")
def home():
    return render_template("index.html")

# --- API
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Flask API DeepEyes UP!"})

@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    results = search_in_embeddings(query)
    return jsonify({"results": results})

@app.route("/api/annotations", methods=["GET", "POST"])
def annotations():
    if request.method == "GET":
        annotations = Annotation.query.all()
        return jsonify([{"id": a.id, "text": a.text} for a in annotations])
    elif request.method == "POST":
        data = request.get_json()
        new_annotation = Annotation(text=data.get("text"))
        db.session.add(new_annotation)
        db.session.commit()
        return jsonify({"status": "annotation added"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
