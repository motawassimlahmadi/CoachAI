import json
from openai import OpenAI
from config import OPENAI_API_KEY
from prompt import PROMPT ,  EXERCICE_PROMPT # C'est le GROS prompt pour la séance JSON
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

client = OpenAI(api_key=OPENAI_API_KEY)


def extract_criteria(user_query: str) -> dict:
    """
    Analyse la requête utilisateur et extrait les critères de recherche au format JSON.
    """
    
    # NOUVEAU PROMPT : simple, juste pour extraire les critères
    CRITERIA_PROMPT = PROMPT
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0  # Température à 0 pour une extraction stricte
    )
    
    messages = [
        SystemMessage(content=CRITERIA_PROMPT),
        HumanMessage(content=user_query)
    ]
    
    try:
        print("--- Requête d'extraction de critères envoyée ---")
        print(f"Question (Utilisateur): {user_query}\n")

        response = llm.invoke(messages)

        print("--- Réponse de l'IA (Critères JSON) ---")
        print(response.content)
        
        # On parse le JSON pour retourner un dict
        criteria_dict = json.loads(response.content)
        return criteria_dict

    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction des critères : {e}")
        return {} # Retourner un dict vide en cas d'échec
    
    
def compose_workout(user_query: str, criteria: dict, exercises: list) -> str:
    """
    Compose une séance d'entraînement JSON structurée à partir de la requête, 
    des critères et d'une liste d'exercices.
    """
    
    # On formate les exercices trouvés pour les injecter dans le prompt
    # On suppose que "objectID" d'Algolia est la "exRef"
    exercise_list_for_prompt = [
        {
            "name": ex.get("nameFr", "Nom inconnu"),
            "exRef": ex.get("objectID", f"/exercices/ref_inconnue"), # Utiliser l'objectID comme ref
            "muscles": ex.get("partiesDuCorps", []),
            "equipment": ex.get("equipment", "")
        } for ex in exercises # Limite à 10 comme dans le code original
    ]

    # Le message système est maintenant le PROMPT détaillé de 'prompt.py'
    system_prompt = EXERCICE_PROMPT

    # Le message utilisateur contextualise la demande
    user_content = f"""
    Voici la demande originale de l'utilisateur :
    "{user_query}"

    Voici les critères que j'ai extraits :
    {json.dumps(criteria, indent=2)}

    Et voici une liste d'exercices pertinents trouvés dans notre base de données (Algolia) que tu peux utiliser :
    {json.dumps(exercise_list_for_prompt, indent=2, ensure_ascii=False)}

    En te basant sur la demande originale et les exercices disponibles, crée la séance d'entraînement complète.
    Tu DOIS suivre à la lettre les instructions de formatage JSON définies dans le message système (ton rôle).
    Assure-toi d'utiliser les `exRef` fournies dans la liste d'exercices ci-dessus.
    Si aucun exercice n'est fourni, crée une séance pertinente (ex: poids du corps) avec des `exRef` plausibles (ex: "/exercices/pompes").
    Retourne UNIQUEMENT le JSON.
    """
    
    print("\n--- Requête de composition de séance (JSON) envoyée ---")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7,
        response_format={"type": "json_object"} # Force la sortie en JSON
    )

    return response.choices[0].message.content