from openai import OpenAI
from services.open_ai_service import analyze_query, compose_workout
from services.algolia_service import search_exercises
from prompt import EXERCICE_PROMPT
import json 

client = OpenAI()


def CoachAI(query):
    
    analysis_query = analyze_query(query)
    
    if not analysis_query:
        print(f"Desolé je n'ai pas pu analyser votre requête : {query}")
        return 
    
    criteria = analysis_query.get("criteria",{})
    seance_info = analysis_query.get("seance",{"types":["seance normale"]})
    exercices = analysis_query.get("Exercices")
    
    print(f"Critères : {criteria}")
    print(f"Seance info : {seance_info}")
    print(f"Exercices : {exercices}")
    
    print("\nRecherche d'exercices...")
    exercises = search_exercises(criteria , query)
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
        print(workout_json_string) 

    return workout_data


def chatbot(messages):
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
        response_format={"type": "json_object"}
    )
    
    answer = response.choices[0].message.content
    
    return answer



def get_system_prompt(current_workout):
    prompt_systeme = (
        "Tu es un coach assistant strict et déterministe.\n"
        "Tu dois TOUJOURS répondre en JSON valide, sans aucun texte en dehors du JSON.\n\n"
        
        "### RÈGLES DE GÉNÉRATION D'ENTRAÎNEMENT :\n"
        f"{EXERCICE_PROMPT}\n\n"

        "RÈGLES FONDAMENTALES SUR 'action' :\n"
        "- Mets \"action\": \"add\" UNIQUEMENT si l'utilisateur demande EXPLICITEMENT "
        "d'AJOUTER un ou plusieurs NOUVEAUX exercices.\n"
        "- Si l'utilisateur ne demande PAS clairement un ajout → mets OBLIGATOIREMENT \"action\": \"none\".\n"
        "- En cas de doute → \"action\": \"none\".\n\n"

        "IMPORTANT (AJOUT) :\n"
        "- Si \"action\" == \"add\", N'AJOUTE JAMAIS les exercices toi-même.\n"
        "- Tu dois SEULEMENT indiquer \"action\": \"add\".\n"
        "- L'ajout réel des exercices sera fait PLUS TARD par le code après une recherche Algolia.\n\n"

        "IMPORTANT (SUPPRESSION) :\n"
        "- Si l'utilisateur demande de supprimer, enlever ou retirer un ou plusieurs exercices :\n"
        "  • mets OBLIGATOIREMENT \"action\": \"none\".\n"
        "  • supprime UNIQUEMENT les exercices explicitement visés par la demande.\n"
        "  • ne supprime JAMAIS d'autres exercices.\n"
        "  • garde la séance STRICTEMENT identique en dehors des exercices supprimés.\n\n"
        
        
        "IMPORTANT (MODIFICATION) :\n"
        "- Si l'utilisateur demande de modifier la séance (exemples : changer les poids, répétitions, repos, tempo, RIR/RPE, passer un ou plusieurs exercices en superset, circuit, AMRAP, interval, etc.) :"

        "• mets OBLIGATOIREMENT \"action\": \"none\".\n"
        "• modifie UNIQUEMENT les éléments explicitement mentionnés par l'utilisateur.\n"
        "• ne modifie JAMAIS :\n"
            "- les exercices non concernés,\n"
            "- les exRef,\n"
            "- l’ordre des exercices (sauf si explicitement demandé).\n"
        "• si un exercice est modifié :\n"
            "- conserve tous ses champs inchangés sauf ceux demandés.\n"
        "• si un changement de structure est demandé (superset, circuit, AMRAP, interval) :\n"
            "- ajoute ou modifie UNIQUEMENT les champs nécessaires (groupId, sectionId, sectionType, etc.).\n"
        "• garde la séance STRICTEMENT identique en dehors des modifications demandées.\n"


        

        "IMPORTANT (INTERDICTIONS) :\n"
        "- Tu n'as PAS le droit d'ajouter d'exercices si \"action\" == \"none\".\n"
        "- Tu n'as PAS le droit d'ajouter d'exercices si \"action\" == \"add\".\n"
        "- Tu n'as PAS le droit d'inventer des exercices.\n\n"

        f"SÉANCE ACTUELLE (SOURCE DE VÉRITÉ) : {json.dumps(current_workout, ensure_ascii=False)}\n\n"

        "FORMAT DE RÉPONSE STRICT (aucune clé supplémentaire autorisée) :\n"
        "{\n"
        "  \"message\": \"résumé court de l'action\",\n"
        "  \"action\": \"add\" | \"none\",\n"
        "  \"workout_mis_a_jour\": { ... séance complète après application exacte de la demande ... }\n"
        "}\n"
        
        
    )
    return prompt_systeme
    

def chatAI(current_workout):
    # Prompt initial
    

    prompt_systeme = get_system_prompt(current_workout)
    

    messages = [{"role": "system", "content": prompt_systeme}]
    
    last_ai_response = None

    while True:
        user_raw_input = input("\nVous (ou 'exit') : ") 
        if user_raw_input.lower() == "exit": 
            break

        messages.append({"role": "user", "content": user_raw_input})
        
        try:
            res_raw = chatbot(messages)
            res_json = json.loads(res_raw)

            # --- LOGIQUE D'AJOUT (Action: add) ---
            if res_json.get("action") == "add":
                # On utilise user_raw_input 
                print(f"--- Recherche d'exercices pour : {user_raw_input} ---")
                new_workout_part = CoachAI(user_raw_input)
                
                
                if new_workout_part and "exercices" in new_workout_part:
                    current_workout["exercices"].extend(new_workout_part["exercices"])
                    if res_json.get("workout_mis_a_jour"):
                        res_raw += str(new_workout_part["exercices"])
                        res_json["workout_mis_a_jour"] = current_workout
                else:
                    print("Aucun exercice trouvé pour cette demande.")

            # --- LOGIQUE DE MISE À JOUR SIMPLE 
            else:
                updated = res_json.get("workout_mis_a_jour")
                if updated:
                    current_workout = updated

            # Affichage de la séance actuelle
            print(json.dumps(current_workout, indent=2, ensure_ascii=False))
            
            if last_ai_response:
                messages.remove(last_ai_response)
            
            
            # MISE À JOUR DU CONTEXTE 
            messages[0]["content"] = get_system_prompt(current_workout)
            
            
            # print(f"res_raw : {res_raw}")
            last_ai_response = {"role": "assistant", "content": res_raw}
            messages.append(last_ai_response)
            
            
        except Exception as e:
            print(f"Erreur : {e}")
        