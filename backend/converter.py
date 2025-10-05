import requests
from app import NASA_API_KEY
from PIL import Image
from io import BytesIO

# Coloque sua chave da NASA aqui
api_key = "2lKrd3NQRCRAadHid5sSA7k0P0pZW5uwr4Lca7BU"

# Endpoint da APOD
url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"

# Faz a requisição
res = requests.get(url)

# Transforma a resposta em JSON
data = res.json()

# Mostra informações importantes
print("Título:", data.get("title"))
print("Data:", data.get("date"))
print("Descrição:", data.get("explanation"))
print("URL da imagem:", data.get("url"))