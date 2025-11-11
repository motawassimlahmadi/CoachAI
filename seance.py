from openai import OpenAI
from config import OPENAI_API_KEY
import numpy as np
import json
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage
from prompt import SEANCE_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)



def seance_similarity(description: str):
    """
    Compare une description de séance à 5 types de séances :
    Séance normale, AMRAP, Interval, Circuit, Superset.
    Renvoie le type le plus similaire et la liste des similarités.
    
    """
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    user_query = description
    
    messages = [
        SystemMessage(content=SEANCE_PROMPT),
        HumanMessage(content=user_query)
    ]
    
    
    
    try:
        print("--- Requête d'extraction des types de séances envoyée ---")
        print(f"Question (Utilisateur): {user_query}\n")

        response = llm.invoke(messages)
        
        # On parse le JSON pour retourner un dict
        criteria_dict = json.loads(response.content)
        return criteria_dict

    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction des critères : {e}")
        return {} # Retourner un dict vide en cas d'échec
    
    


# Exemple d’utilisation
if __name__ == "__main__":
    desc = "Je veux une séance pec/epaule . Je veux faire deux exos pecs en AMRAP et deux exos epaules en superset"
    print(seance_similarity(desc))
    
