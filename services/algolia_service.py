from algoliasearch.search_client import SearchClient
from config import ALGOLIA_APP_ID, ALGOLIA_API_KEY, ALGOLIA_INDEX_NAME

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
index = client.init_index(ALGOLIA_INDEX_NAME)

def search_exercises(criteria: dict):
    filters = []
    muscle_filters = []
    
    if "partiesDuCorps" in criteria and criteria["partiesDuCorps"]:
        for muscle in criteria["partiesDuCorps"]:
            muscle_filters.append(f'partiesDuCorps:{muscle}')
             
    
    if "equipment" in criteria and criteria["equipment"]:
        filters.append(f'equipment:"{criteria["equipment"]}"')
        
    if "discipline" in criteria and criteria["discipline"]:
        filters.append(f'discipline:"{criteria['discipline']}"')

    if "brand" in criteria and criteria["brand"]:
        filters.append(f'brand:"{criteria['brand']}"')
        
    
    if len(criteria["partiesDuCorps"]) >= 2:
        # Regroupe plusieurs muscles avec OR
        muscle_filter_str = " OR ".join(muscle_filters)
        # Ajoute des parenthèses pour éviter les ambiguïtés dans Algolia
        filter_str = f"({muscle_filter_str}) AND " + " AND ".join(filters)
    else:
        # Si un seul ou aucun muscle, on n’ajoute que les autres filtres
        filter_str = " AND ".join(filters)
    
    
    print(f"--- Filtre Algolia --- \n{filter_str}")
    
    results = index.search("", {"filters": filter_str, "hitsPerPage": 10})
    return results["hits"]