from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from datetime import datetime

db = SQLAlchemy()

# ----- Tabela de anotações -----
class Annotation(db.Model):
    __tablename__ = "annotations"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    image_id = db.Column(db.Integer, db.ForeignKey("satellite_images.id"), nullable=True)


# ----- Tabela de imagens de satélite -----
class SatelliteImage(db.Model):
    __tablename__ = "satellite_images"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(Geometry("POINT"))
    description = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)
    source = db.Column(db.String(100))
    url = db.Column(db.String(300), nullable=True)  # link da imagem
    annotations = db.relationship("Annotation", backref="image", lazy=True)



# ----- Cache de imagens -----
class ImageCache(db.Model):
    """
    Tabela simples pra controle do cache (opcional),
    útil pra mapear o que está no Redis.
    """
    __tablename__ = "image_cache"
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("satellite_images.id"), unique=True)
    cached_key = db.Column(db.String(200), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
