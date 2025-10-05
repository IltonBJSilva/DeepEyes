from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()

# ----- Tabela de anotações -----
class Annotation(db.Model):
    __tablename__ = "annotations"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    # opcional: associar a uma imagem geoespacial
    image_id = db.Column(db.Integer, db.ForeignKey("satellite_images.id"), nullable=True)


# ----- Tabela de imagens de satélite -----
class SatelliteImage(db.Model):
    __tablename__ = "satellite_images"
    id = db.Column(db.Integer, primary_key=True)
    # localizacao geoespacial (POINT)
    location = db.Column(Geometry("POINT"))
    description = db.Column(db.String(500))
    # campos extras que podem ser úteis
    timestamp = db.Column(db.DateTime)
    source = db.Column(db.String(100))  # ex: NASA, INPE, TESS, etc.
    
    # relacionamento com annotations
    annotations = db.relationship("Annotation", backref="image", lazy=True)
