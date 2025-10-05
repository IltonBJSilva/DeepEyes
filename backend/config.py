import os

# URL do Neon PostgreSQL
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_iXUr9zeV1xEa@ep-weathered-fog-acqya7nv-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Chave secreta
api_nasa = os.environ.get("api_nasa", "deepeyes-secret")
