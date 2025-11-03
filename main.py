from services.open_ai_service import extract_criteria, compose_workout
from services.algolia_service import search_exercises
import json 

def main():
    print("=== Assistant IA Coach ===")
    query = input("Entre ta demande : ")

    print("\n📊 Analyse de la requête...")
    criteria = extract_criteria(query) # Retourne maintenant un dict
    
    if not criteria:
        print("Désolé, je n'ai pas pu analyser les critères de votre requête.")
        return

    print(f"Critères extraits: {criteria}")

    print("\nRecherche d'exercices...")
    exercises = search_exercises(criteria)
    print(f"{len(exercises)} exercices trouvés")
    

    if not exercises:
        print("Aucun exercice trouvé pour ces critères. Tentative de génération d'une séance par défaut...")

    print("\nGénération de la séance (JSON)...")
    # On passe la 'query' originale en plus des critères et exercices
    workout_json_string = compose_workout(query, criteria, exercises)
    
    print("\n=== Séance JSON générée ===")
    try:
        # On parse le JSON pour l'afficher joliment (pretty-print)
        workout_data = json.loads(workout_json_string)
        print(json.dumps(workout_data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("--- Erreur: L'IA n'a pas retourné un JSON valide ---")
        print(workout_json_string) # Affiche la sortie brute pour le débogage

if __name__ == "__main__":
    main()