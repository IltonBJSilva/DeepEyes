async function doSearch() {
    const query = document.getElementById("searchBox").value;
    const resultsList = document.getElementById("results");
    resultsList.innerHTML = "<li class='list-group-item'>Buscando...</li>";

    try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        resultsList.innerHTML = "";
        if (data.results.length === 0) {
            resultsList.innerHTML = "<li class='list-group-item'>Nenhum resultado encontrado.</li>";
            return;
        }

        data.results.forEach(item => {
            const li = document.createElement("li");
            li.className = "list-group-item";

            // Texto
            const textNode = document.createElement("p");
            textNode.textContent = item.text;
            li.appendChild(textNode);

            // Imagem, se existir
            if (item.image_url) {
                const img = document.createElement("img");
                img.src = item.image_url;
                img.className = "img-fluid mt-2";
                img.style.maxHeight = "300px";
                li.appendChild(img);
            }

            resultsList.appendChild(li);
        });
    } catch (err) {
        console.error(err);
        resultsList.innerHTML = "<li class='list-group-item text-danger'>Erro ao buscar!</li>";
    }
}
