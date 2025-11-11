from services.open_ai_service import analyze_query, compose_workout
from services.algolia_service import search_exercises
import json 
from prompt import PROMPT_INTRODUCTION

def main():
    print(PROMPT_INTRODUCTION)
    
    # 1ere étape : Query de l'utilisateur
    
    query = input("Entre ta demande : ")
    print("\n📊 Analyse de la requête...")
    
    # Fin DE LA PREMIERE ETAPE -----------------------------
    
    # 2eme etape : Critère et type de seance
    
    analysis_query = analyze_query(query)
    
    if not analysis_query:
        print(f"Desolé je n'ai pas pu analyser votre requête : {query}")
        return 
    
    criteria = analysis_query.get("criteria",{})
    seance_info = analysis_query.get("seance",{"types":["seance normale"]})
    exercices = analysis_query.get("Exercices",{"Nombre" : [4]})
    
    print(f"Critères : {criteria}")
    print(f"Seance info : {seance_info}")
    print(f"Exercices : {exercices}")
    
    
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
    workout_json_string = compose_workout(query, criteria, exercises , seance_info , exercices)
    
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