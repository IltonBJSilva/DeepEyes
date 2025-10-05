async function doSearch() {
    const query = document.getElementById("searchBox").value;
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p class='text-center'>Buscando...</p>";

    try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        resultsDiv.innerHTML = "";
        if (data.results.length === 0) {
            resultsDiv.innerHTML = "<p class='text-center'>Nenhum resultado encontrado.</p>";
            return;
        }

        // Cria carrossel
        const carouselId = "searchCarousel";
        const indicators = [];
        const slides = [];

        data.results.forEach((item, index) => {
            indicators.push(`
                <button type="button" data-bs-target="#${carouselId}" data-bs-slide-to="${index}" 
                    class="${index === 0 ? 'active' : ''}" aria-current="${index === 0 ? 'true' : 'false'}" 
                    aria-label="Slide ${index+1}"></button>
            `);

            slides.push(`
                <div class="carousel-item ${index === 0 ? 'active' : ''}">
                    ${item.image_url ? `<img src="${item.image_url}" class="d-block w-100 rounded" style="max-height:500px; object-fit:contain;" alt="Imagem">` : ""}
                    <div class="carousel-caption d-none d-md-block bg-dark bg-opacity-50 rounded p-2">
                        <h5>${item.text || "Sem título"}</h5>
                        <p>${item.source || ""}</p>
                    </div>
                </div>
            `);
        });

        resultsDiv.innerHTML = `
            <div id="${carouselId}" class="carousel slide" data-bs-ride="carousel">
                <div class="carousel-indicators">
                    ${indicators.join('')}
                </div>
                <div class="carousel-inner">
                    ${slides.join('')}
                </div>
                <button class="carousel-control-prev" type="button" data-bs-target="#${carouselId}" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Anterior</span>
                </button>
                <button class="carousel-control-next" type="button" data-bs-target="#${carouselId}" data-bs-slide="next">
                    <span class="carousel-control-next-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Próximo</span>
                </button>
            </div>
        `;

    } catch (err) {
        console.error(err);
        resultsDiv.innerHTML = "<p class='text-danger text-center'>Erro ao buscar!</p>";
    }
}

// Enter dispara a busca
document.getElementById("searchBox").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        doSearch();
    }
});
