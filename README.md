# CoachAI

Assistant coach sportif intelligent qui génère des programmes d'entraînement personnalisés via une conversation naturelle, en s'appuyant sur GPT-4 et une base d'exercices indexée sur Algolia.

---

## Fonctionnement

1. L'utilisateur décrit sa séance souhaitée en langage naturel ("je veux travailler les pectoraux avec haltères, niveau intermédiaire")
2. Le système **analyse la requête** pour extraire les groupes musculaires, l'équipement, le type de séance et le niveau
3. Une **recherche Algolia** récupère les exercices correspondants depuis la base de données
4. GPT-4 **compose un programme structuré** avec séries, répétitions, charges et temps de repos
5. L'utilisateur peut **affiner la séance** via une conversation interactive

---

## Architecture

```
CoachAI/
├── main.py          # Point d'entrée CLI — boucle conversationnelle
├── api_main.py      # API FastAPI — endpoint POST /generate-workout
├── chatbot.py       # Logique principale : analyse, recherche, composition
├── prompt.py        # Prompts système (analyse, composition, introduction)
├── config.py        # Chargement des variables d'environnement
├── services/        # Intégrations externes (OpenAI, Algolia, Firebase)
└── requirements.txt
```

---

## Types de séances supportés

| Type | Description |
|---|---|
| Standard | Sets × reps classiques avec progression pyramidale |
| Superset | 2 exercices enchaînés, sets synchronisés |
| Circuit | 4+ exercices en rotation |
| AMRAP | Maximum de rounds en temps limité |
| Interval | Travail / repos chronométrés |

---

## Stack technique

- **LLM** : OpenAI GPT-4 (via `openai`)
- **Recherche d'exercices** : Algolia (`algoliasearch>=3.0,<4.0`)
- **Backend API** : FastAPI
- **Base de données** : Firebase Admin
- **Orchestration** : LangChain
- **Config** : python-dotenv

---

## Installation

```bash
git clone https://github.com/motawassimlahmadi/CoachAI.git
cd CoachAI
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine :

```env
OPENAI_API_KEY=your_openai_key
ALGOLIA_APP_ID=your_algolia_app_id
ALGOLIA_API_KEY=your_algolia_api_key
ALGOLIA_INDEX_NAME=your_index_name
FIREBASE_CREDENTIALS=path/to/firebase_credentials.json
```

---

## Utilisation

### Mode CLI

```bash
python main.py
```

### Mode API

```bash
uvicorn api_main:app --reload
```

Endpoint disponible :

```
POST /generate-workout
Body: { "query": "séance jambes avec machines, 45 minutes, niveau débutant" }
```

---

## Exemple de sortie

```json
{
  "sections": [
    {
      "sectionType": "standard",
      "exercises": [
        {
          "name": "Squat Presse",
          "perfControllers": [12, 10, 8, 6],
          "weightControllers": [60, 70, 80, 90],
          "restPause": 90
        }
      ]
    }
  ]
}
```
