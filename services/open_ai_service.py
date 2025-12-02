import json
from openai import OpenAI
from config import OPENAI_API_KEY
from prompt import ANALYSIS_PROMPT , EXERCICE_PROMPT
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_query(query:str) -> dict :
    
    """
    Analyse la requête utilisateur et extrait les critères de recherche au format JSON.
    
    """
    
    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0.2
    )
    
    messages = [
        SystemMessage(content=ANALYSIS_PROMPT),
        HumanMessage(content=query)
    ]
    
    try:
        response = llm.invoke(messages)
        
        result = json.loads(response.content)
        
        return result
    except Exception as e :
        print(f"Une erreur s'est produite lors de l'extraction des critères : {e}")
        return {} 

    

def compose_workout(user_query: str, criteria: dict, exercises: list , seance_type:str , nombre_exercice : str) -> str:
    """
    Compose une séance d'entraînement JSON structurée à partir de la requête, 
    des critères et d'une liste d'exercices.
    """
    
    # On formate les exercices trouvés pour les injecter dans le prompt
    # On suppose que "objectID" d'Algolia est la "exRef"
    exercise_list_for_prompt = [
        {
            "exRef": ex.get("objectID", f"/exercices/ref_inconnue"), # Utiliser l'objectID comme ref
            "muscles": ex.get("partiesDuCorps", []),
            "equipment": ex.get("equipment", ""),
            "brand":ex.get("brand","")
        } for ex in exercises 
    ]
    
    print(exercise_list_for_prompt)

    # Le message système
    system_prompt = EXERCICE_PROMPT

    
    user_content = f"""
    Voici la demande originale de l'utilisateur :
    "{user_query}"

    Voici les critères que j'ai extraits :
    {json.dumps(criteria, indent=2)}
    
    Voici le nombre d'exercice pour la séance:
    {nombre_exercice}
    
    Voici le type de séance à impérativement utiliser :
    {seance_type}

    Et voici une liste d'exercices pertinents trouvés dans notre base de données (Algolia) que tu peux utiliser :
    {json.dumps(exercise_list_for_prompt, indent=2, ensure_ascii=False)}

    En te basant sur la demande originale et les exercices disponibles, crée la séance d'entraînement complète en te basant sur {seance_type}
    Tu DOIS suivre à la lettre les instructions de formatage JSON définies dans le message système (ton rôle).
    Assure-toi d'utiliser les `exRef` fournies dans la liste d'exercices ci-dessus dans le format suivant "/exercices/exRef" où exRef est le objectID.
    NB : exRef doit OBLIGATOIREMENT être un objectID type : "MtR6kf74Mq8LQwpGYJ2f" .
    Si aucun exercice n'est fourni, crée une séance pertinente à partir de {seance_type} avec des `exRef` plausibles (ex: "/exercices/pompes").
    Dans le cas où aucun exercice n'est fourni et uniquement dans ce cas précise que l'exercice n'est pas tiré de la base de données.
    Il est extremement important de generer exactement {nombre_exercice} 
    Retourne UNIQUEMENT le JSON.
    """
    
    print("\n--- Requête de composition de séance (JSON) envoyée ---")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.4,
        response_format={"type": "json_object"} # Force la sortie en JSON
    )

    return response.choices[0].message.content