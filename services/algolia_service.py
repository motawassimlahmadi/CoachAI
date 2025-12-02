from algoliasearch.search_client import SearchClient
from config import ALGOLIA_APP_ID, ALGOLIA_API_KEY, ALGOLIA_INDEX_NAME

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
index = client.init_index(ALGOLIA_INDEX_NAME)



def search_exercises(criteria: dict, search_query: str):
    """
    Recherche intelligente avec gestion dynamique des filtres et facettes.
    
    """
    
    # 1. Préparation des Facet Filters (Syntaxe tableau d'Algolia)
    # La structure : [FILTER_AND, [FILTER_OR_1, FILTER_OR_2], FILTER_AND]
    facet_filters = []

    fields_map = {
        "partiesDuCorps": "partiesDuCorps",
        "equipment": "equipment",
        "discipline": "discipline",
        "brand": "brand"
    }

    for key, algolia_attr in fields_map.items():
        value = criteria.get(key)
        
        if value:
            # Si c'est une liste (ex: plusieurs muscles), on crée un sous-tableau (Logique OR)
            if isinstance(value, list):
                or_filters = [f"{algolia_attr}:{item}" for item in value]
                facet_filters.append(or_filters)
            # Si c'est une valeur simple, on l'ajoute directement (Logique AND implicite)
            else:
                facet_filters.append(f"{algolia_attr}:{value}")

    # 2. Configuration de la recherche
    search_params = {
        "facetFilters": facet_filters,
        "hitsPerPage": 30
    }

    if facet_filters:
        print(f"--- Filtres Actifs (Facets) --- \n{facet_filters}")


    try:
        search_query = ""
        results = index.search(search_query, search_params)
        if len(results["hits"]) > 0:
            return results["hits"]
        else:
            results = index.search(search_query)
            return results["hits"]
    except Exception as e:
        print(f"Erreur Algolia : {e}")
        return []


