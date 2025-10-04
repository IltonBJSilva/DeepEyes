from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# ----- CONFIGURAÇÃO SIMULADA -----
SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
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

# ----- DB & CORS -----
db = SQLAlchemy(app)
CORS(app)

# ----- MODELO -----
class Annotation(db.Model):
    __tablename__ = "annotations"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))

# ----- FUNÇÃO SIMULADA DE BUSCA -----
def search_in_embeddings(query):
    return [{"id": 1, "text": f"Resultado simulado para '{query}'"}]

# ⚡ Cria tabelas no contexto do app
with app.app_context():
    db.create_all()

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

# ----- RODAR LOCAL -----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
