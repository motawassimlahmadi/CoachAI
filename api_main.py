from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from services.open_ai_service import analyze_query, compose_workout
from services.algolia_service import search_exercises

# Initialisation
app = FastAPI()


# GESTION DU CORS
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",  # L'URL du site JS en dev
    "https://votre-app-client.com",  # L'URL du site JS en production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Autorise ces origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],
)


# On envoie seulement la query de l'utilisateur , rien de plus 
class WorkoutRequest(BaseModel):
    query: str
    

@app.post("/generate-workout")
async def generate_workout_endpoint(request: WorkoutRequest):
    """
    Cet endpoint prend une requête utilisateur, analyse les critères,
    recherche des exercices et compose une séance.
    """
    print(f"Requête reçue pour : {request.query}")
    
    
    try:
        analysis_query = analyze_query(request.query) # Analyse de la query 
        
        criteria = analysis_query.get("criteria",{})
        seance_info = analysis_query.get("seance",{"types":["seance normale"]})
        exercices = analysis_query.get("Exercices",{"Nombre" : [4]})
        

        if not analysis_query:
            print(f"Desolé je n'ai pas pu analyser votre requête : {request.query}")
            return 
        
    except Exception as e:
        print(f"Erreur d'analyse : {e}")
        raise HTTPException(status_code=400, detail=f"Erreur d'analyse IA: {e}")

    # 3. Rechercher les exercices
    try:
        
        print("\nRecherche d'exercices...")
        exercises = search_exercises(criteria)
        print(f"{len(exercises)} exercices trouvés")
        
        
    except Exception as e:
        print(f"Erreur Algolia : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche d'exercices.")

    # 4. Composer la séance
    try:
        # On passe la 'query' originale en plus des critères et exercices
        workout_json_string = compose_workout(request.query, criteria, exercises , seance_info , exercices)
        
        # Convertir la string JSON en objet Python (dict) pour le retour
        workout_data = json.loads(workout_json_string)
        
        return workout_data

    except json.JSONDecodeError:
        print("Erreur: L'IA n'a pas retourné un JSON valide")
        raise HTTPException(status_code=500, detail="Erreur de génération de séance (format JSON invalide).")
    except Exception as e:
        print(f"Erreur de composition : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de composition de la séance: {e}")

# --- Endpoint de test pour vérifier que le serveur est en ligne ---
@app.get("/")
def read_root():
    return {"status": "API de fitness en ligne !"}