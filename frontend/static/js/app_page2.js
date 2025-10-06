const canvas = document.getElementById('planetCanvas');
const ctx = canvas.getContext('2d');

canvas.width = 400;
canvas.height = 400;

const planetImg = new Image();
planetImg.src = 'earth.jpg'; // coloque sua textura aqui

let rotation = 0;

function drawPlanet() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.translate(canvas.width/2, canvas.height/2);
  ctx.rotate(rotation);
  ctx.drawImage(planetImg, -planetImg.width/2, -planetImg.height/2);
  ctx.restore();
}

// Rotação contínua + scroll
function animate() {
  rotation += 0.002; // rotação contínua
  drawPlanet();
  requestAnimationFrame(animate);
}

// Scroll altera rotação
window.addEventListener('scroll', () => {
  const scroll = window.scrollY;
  rotation = scroll * 0.005; // ajuste velocidade
});

planetImg.onload = () => {
  animate();
};

// ======= Load NASA Image Dynamically =======
fetch('/api/nasa-random')
  .then(response => response.json())
  .then(data => {
    const planet = document.getElementById('planet');
    const image = data.image?.image_url;
    const title = data.image?.title || "NASA Image";
    
    if (image) {
      planet.src = image;
      planet.alt = title;
      planet.style.display = 'block'; // mostra quando carregar
    } else {
      planet.style.display = 'none';
      console.warn("Nenhuma imagem encontrada na API NASA");
    }
  })
  .catch(err => {
    console.error("Erro ao buscar imagem da NASA:", err);
  });