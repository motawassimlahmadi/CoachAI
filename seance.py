from openai import OpenAI
from config import OPENAI_API_KEY
import numpy as np
import json

client = OpenAI(api_key=OPENAI_API_KEY)


def euclidean_similarity(a, b):
    return 1 / (1 + np.linalg.norm(a - b))


def pearson_similarity(a, b):
    return np.corrcoef(a, b)[0, 1]

def seance_similarity(description: str):
    """
    Compare une description de séance à 5 types de séances :
    Séance normale, AMRAP, Interval, Circuit, Superset.
    Renvoie le type le plus similaire et la liste des similarités.
    """

    # --- Base de référence sous forme de JSON (dictionnaires Python) ---
    types_seances = [
        {
            "type": "Séance normale",
            "description": (
                "Séance classique avec un enchaînement d’exercices planifiés. "
                "Aucun enchainement précis indiqué . On veut juste une séance de sport classique ."
            )
        },
        {
            "type": "AMRAP",
            "description": (
                "Séance où l’on effectue le maximum de tours ou répétitions dans un temps donné. "
                "L’intensité est élevée et l’objectif est d’améliorer l’endurance musculaire et cardiovasculaire."
            ),
            "exemples_phrases": [
                "Je veux faire un maximum de squats, pompes et abdos en 10 minutes.",
                "Faire le plus de tours possible avant la fin du chrono.",
                "Je cherche un entraînement très intense et rapide."
            ],
            "mots_cles": ["AMRAP", "maximum", "tours", "répétitions", "temps limité", "intensité élevée", "endurance"]
        },
        {
            "type": "Interval",
            "description": (
                "Séance basée sur l’alternance d’efforts intenses et de périodes de récupération courte. "
                "Objectif : améliorer la capacité cardiovasculaire, la puissance et la tolérance à l’effort."
            ),
            "exemples_phrases": [
                "Je veux faire des sprints de 30 secondes suivis de 30 secondes de repos.",
                "Séance de HIIT pour améliorer ma condition physique rapidement.",
                "Alterner effort intense et récupération courte."
            ],
            "mots_cles": ["intervalle", "HIIT", "sprint", "repos court", "effort intense", "cardio", "puissance"]
        },
        {
            "type": "Circuit",
            "description": (
                "Suite d’exercices réalisés les uns à la suite des autres, souvent sur différents groupes musculaires. "
                "Repos court entre les exercices et repos plus long après un tour complet. "
                "Objectif : endurance musculaire et cardiovasculaire globale."
            ),
            "exemples_phrases": [
                "Faire un tour complet de 5 exercices sans repos entre eux.",
                "Séance complète du corps avec différents exercices enchaînés.",
                "Je veux un entraînement dynamique avec peu de repos."
            ],
            "mots_cles": ["circuit", "enchaînement", "tour", "repos court", "corps complet", "endurance", "musculaire", "cardio"]
        },
        {
            "type": "Superset",
            "description": (
                "Les supersets sont une technique d’intensification en musculation consistant à enchaîner plusieurs exercices sans temps de repos entre eux. "
                "Cette méthode vise à augmenter la densité et l’intensité de la séance, tout en maximisant le travail musculaire sur un temps réduit. "
                "Un superset classique fait souvent intervenir deux exercices ciblant des groupes musculaires antagonistes (ex : biceps/triceps) ou complémentaires (ex : développé couché/pompes). "
                "Le terme 'superset' est parfois utilisé pour décrire tout enchaînement d’exercices, mais il existe plusieurs variantes comme les bisets (deux exercices sur un même muscle) "
                "et les trisets (trois exercices successifs). Ces techniques visent à choquer le muscle pour favoriser sa croissance et son adaptation rapide."
            ),
            "exemples_phrases": [
                "Je veux enchaîner muscle1 et muscle2 sans repos.",
                "Fais-moi une séance avec des supersets pour les pectoraux et le dos.",
                "Je veux augmenter l’intensité avec des enchaînements d’exercices sans pause."
                
            ],
            "mots_cles": [
                "superset", "enchaînement", "sans repos", "muscles opposés", "agoniste",
                "antagoniste", "densité", "intensité", "biset", "triset",
                "congestion", "gain de temps"
            ]
        }

    ]

    # --- Conversion du JSON en texte avant envoi ---
    json_texts = [json.dumps(t, ensure_ascii=False) for t in types_seances]

    # --- Génération des embeddings ---
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=[description] + json_texts
    )

    embeddings = [np.array(item.embedding) for item in response.data]

    desc_vec = embeddings[0]
    type_vecs = embeddings[1:]

    # --- Calcul des similarités cosinus ---
    similarities = [
        np.dot(desc_vec, t) / (np.linalg.norm(desc_vec) * np.linalg.norm(t))
        for t in type_vecs
    ]
    
    euclidian = [euclidean_similarity(desc_vec,t) for t in type_vecs]
    
    max_euclidian = int(np.argmax(euclidian))

    max_index = int(np.argmax(similarities))

    # --- Retour du type et des scores ---
    return types_seances[max_index]["type"] , types_seances[max_euclidian]["type"]


# Exemple d’utilisation
if __name__ == "__main__":
    desc = "Je veux une séance pec/epaule . Je veux les machines technogym et je veux enchainer les exos"
    print(seance_similarity(desc))
    
