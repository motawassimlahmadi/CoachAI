from services.open_ai_service import extract_criteria, compose_workout
from services.algolia_service import search_exercises
import json 
from seance import seance_similarity

def main():
    print("=== Assistant IA Coach ===")
    
    # 1ere étape : Query de l'utilisateur
    
    query = input("Entre ta demande : ")
    print("\n📊 Analyse de la requête...")
    
    # Fin DE LA PREMIERE ETAPE -----------------------------
    
    # 2eme etape : Critère 
    criteria = extract_criteria(query) # Retourne les critères pour la séance
    type_seance = seance_similarity(query) # Retourne la séance propice pour l'entrainement.
    
    if not criteria:
        print("Désolé, je n'ai pas pu analyser les critères de votre requête.")
        return

    print(f"Critères extraits: {criteria}")
    print(f"Séance extraite : {type_seance}")
    
    # FIN DE LA 2EME ETAPE -----------------------------


    # 3EME RECHERCHE DES EXERCICES SUR ALGOLIA 
    
    
    print("\nRecherche d'exercices...")
    exercises = search_exercises(criteria)
    print(f"{len(exercises)} exercices trouvés")
    

    if not exercises:
        print("Aucun exercice trouvé pour ces critères. Tentative de génération d'une séance par défaut...")

    print("\nGénération de la séance (JSON)...")
    
    
    
    
    # FIN DE LA RECHERCHE -----------------------------
    
    
    # On passe la 'query' originale en plus des critères et exercices
    workout_json_string = compose_workout(query, criteria, exercises , type_seance)
    
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