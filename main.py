from services.open_ai_service import analyze_query, compose_workout
from services.algolia_service import search_exercises
from chatbot import CoachAI , chatAI
import json 
from prompt import PROMPT_INTRODUCTION

def main():
    
    
    print(PROMPT_INTRODUCTION)
    

if __name__ == "__main__":
    main()
    
    query = input("Entre ta demande de séance : ")
    
    # 1. Génération de la séance initiale via les services (Algolia + OpenAI)
    workout = CoachAI(query)
    
    if workout:
        print("\n--- La séance a été générée. Vous pouvez maintenant en discuter avec le coach. ---")
        # 2. Lancement du mode discussion avec la séance en mémoire
        chatAI(workout)
    else:
        print("Erreur lors de la génération de la séance.")