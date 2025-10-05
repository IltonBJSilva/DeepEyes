import requests
from PIL import Image

api_key = "CHAVE"

url = f"https://api.nasa.gov/planetary/apod?api_key=CHAVE"

res = requests.get(url).json()

print("Título:", res['title'])
print("Data:", res['date'])
print("Descrição:", res['explanation'])
print("URL da imagem:", res['url'])

img_url = res['url']
img_data = requests.get(img_url).content

with open("nasa_apod.jpg", "wb") as f:
    f.write(img_data)

    print("Salvameto concluido")


