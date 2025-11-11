from algoliasearch.search_client import SearchClient
from config import ALGOLIA_APP_ID, ALGOLIA_API_KEY, ALGOLIA_INDEX_NAME

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
index = client.init_index(ALGOLIA_INDEX_NAME)



def search_exercises(criteria: dict):
    all_filters = []
    
    # 1. Filtre Muscles (avec OR)
    if "partiesDuCorps" in criteria and criteria["partiesDuCorps"]:
        muscle_filters = [f'partiesDuCorps:{muscle}' for muscle in criteria["partiesDuCorps"]]
        all_filters.append(f"({ ' OR '.join(muscle_filters) })") 
             
    # 2. Autres filtres (avec AND)
    if "equipment" in criteria and criteria["equipment"]:
        all_filters.append(f'equipment:"{criteria["equipment"]}"')
        
    if "discipline" in criteria and criteria["discipline"]:
        all_filters.append(f'discipline:"{criteria["discipline"]}"')

    if "brand" in criteria and criteria["brand"]:
        all_filters.append(f'brand:"{criteria["brand"]}"')
        
    
    # if "difficulty" in criteria and criteria["difficulty"]:
    #     all_filters.append(f'difficulty:"{criteria["difficulty"]}"')

    # Combine tous les filtres avec AND
    filter_str = " AND ".join(all_filters)
    
    if filter_str:
        print(f"--- Filtre Algolia --- \n{filter_str}")
    
    results = index.search("", {"filters": filter_str, "hitsPerPage": 30})
    return results["hits"]