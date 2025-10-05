from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

# ----- Tabela de anotações -----
class Annotation(db.Model):
    __tablename__ = "annotations"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    image_id = db.Column(db.Integer, db.ForeignKey("satellite_images.id"), nullable=True)



class SatelliteImage(db.Model):
    __tablename__ = "satellite_images"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    location = db.Column(Geometry("POINT"))
    timestamp = db.Column(db.DateTime)
    source = db.Column(db.String)
    url = db.Column(db.String)
    embedding = db.Column(JSON)  # Campo para embedding do texto da descrição




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
