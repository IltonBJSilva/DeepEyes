import json

def search_in_embeddings(query):
    cache_key = f"search:{query.lower()}"
    cached = get_cached_image(cache_key)
    if cached:
        return json.loads(cached.decode("utf-8"))
    results = [{"id": 1, "text": f"Resultado simulado para '{query}'"}]
    set_cached_image(cache_key, json.dumps(results).encode("utf-8"))
    return results
