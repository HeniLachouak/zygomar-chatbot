# Professeur Zygomar 🤯

    C'est un chatbot web humoristique et éducatif conçu pour offrir une expérience d’interaction unique grâce à une personnalité volontairement excentrique, drôle et légèrement « à côté de la plaque ». Malgré son ton absurde, il est capable de fournir de vraies réponses utiles grâce au modèle d’IA .

## Lancer rapidement (local)

### Prérequis

- Python 3.10+
- Un compte [Groq](https://console.groq.com/keys) → clé gratuite
- Un compte [OpenRouter](https://openrouter.ai/keys) → clé gratuit

#### Étapes

1. Clone le repo
2. Crée un fichier .env
   OPENROUTER_API_KEY=sk-or-XXXXXXXXXXXXXXXXXXXXXXXX
   GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
3. Installe les dépendances
   pip install -r requirements.txt
4. Lance le serveur :
   python chatbot_server.py
5. Ouvre ton navigateur
   → http://localhost:8000

Parle → Zygomar répond vocalement !

##### Technologies utilisées

Backend : Flask + Gunicorn
Transcription vocale : Groq Whisper (distil-whisper-large-v3 ou whisper-large-v3)
Génération texte : OpenRouter (amazon/nova-2-lite-v1:free ou tout autre modèle)
Frontend : HTML/CSS/JS pur (zéro framework)
Conteneur : Docker + multi-stage build

###### l'app est Déplé sur Docker

👨‍💻 Auteur

Projet développé par Heni Lachouak, ingénieur IA & data science.

📄 Licence

Projet open-source. Tu peux le modifier, l’améliorer ou le transformer selon tes besoins.
