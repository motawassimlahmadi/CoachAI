from algoliasearch.search_client import SearchClient
from config import ALGOLIA_APP_ID, ALGOLIA_API_KEY, ALGOLIA_INDEX_NAME

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
index = client.init_index(ALGOLIA_INDEX_NAME)

def search_exercises(criteria: dict):
    filters = []
    
    if "partiesDuCorps" in criteria and criteria["partiesDuCorps"]:
        for muscle in criteria["partiesDuCorps"]:
            filters.append(f"partiesDuCorps:{muscle}") 
    
    if "equipment" in criteria and criteria["equipment"]:
        filters.append(f'equipment:"{criteria["equipment"]}"')
        
    if "discipline" in criteria and criteria["discipline"]:
        filters.append(f'discipline:"{criteria['discipline']}"')

    if "brand" in criteria and criteria["brand"]:
        filters.append(f'brand:"{criteria['brand']}"')
    
    filter_str = " AND ".join(filters)
    
    print(f"--- Filtre Algolia --- \n{filter_str}")
    
    results = index.search("", {"filters": filter_str, "hitsPerPage": 10})
    return results["hits"]