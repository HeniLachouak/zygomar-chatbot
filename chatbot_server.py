# chatbot_server.py
import os
import re
import io
import requests
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

# === CLÉS API ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # ← Clé gratuite Groq

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY manquante dans le .env")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY manquante → crée une clé gratuite ici : https://console.groq.com/keys")

# Client OpenRouter (pour le texte du Professeur Zygomar)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

CONVERSATIONS = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Tu es Professeur Zygomar, philosophe du dimanche et maître des digressions absurdes. "
        "Ne réponds jamais directement aux questions, mais fais des phrases courtes et drôles, "
        "en évitant les caractères spéciaux (*, #, <, >) et le texte formaté. "
        "Fais des réponses punchy et lisibles, maximum 2-3 phrases."
    )
}

def clean_text(text):
    text = re.sub(r"[*#<>_`]", "", text)
    text = re.sub(r"\s+", " ", text)
    if len(text) > 300:
        text = text[:300] + "…"
    return text.strip()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/static/avatar.png')
def serve_avatar_png():
    root_avif = os.path.join(app.root_path, "avatar.avif")
    if os.path.exists(root_avif):
        return send_from_directory(app.root_path, "avatar.avif")
    fallback = os.path.join(app.root_path, "static", "avatar.png")
    if os.path.exists(fallback):
        return send_from_directory(os.path.join(app.root_path, "static"), "avatar.png")
    abort(404)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    session_id = data.get("session_id", "default")
    user_text = data.get("user_message", "").strip()
    if not user_text:
        return jsonify({"error": "user_message vide"}), 400

    history = CONVERSATIONS.setdefault(session_id, [])
    if not history:
        history.append(SYSTEM_PROMPT)

    history.append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model="amazon/nova-2-lite-v1:free",
            messages=history,
            extra_body={"reasoning": {"enabled": True}},
        )
        assistant_msg = response.choices[0].message
        cleaned_reply = clean_text(assistant_msg.content)

        history.append({"role": "assistant", "content": assistant_msg.content})
        
        return jsonify({
            "reply": cleaned_reply,
            "session_id": session_id
        })

    except Exception as e:
        logging.exception("Erreur OpenRouter")
        return jsonify({"error": "API OpenRouter HS", "details": str(e)}), 502


# ==================== TRANSCRIPTION AVEC GROQ (CORRIGÉ : files vs data) ====================
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "audio_file" not in request.files:
        return jsonify({"transcription": "Aucun audio reçu"}), 400

    audio_file = request.files["audio_file"]
    audio_bytes = audio_file.read()

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            files={
                "file": ("voice.webm", audio_bytes, "audio/webm")  # ← Seulement l'audio ici
            },
            data={  # ← Les params (model, etc.) ICI, pas dans files !
                "model": "whisper-large-v3",  # Ou "whisper-large-v3-turbo" pour + rapide
                "language": "fr",
                "response_format": "json",
                "temperature": "0.0"
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()
        text = result.get("text", "").strip()

        if not text:
            text = "(silence détecté)"

        return jsonify({"transcription": text})

    except requests.exceptions.HTTPError as e:
        logging.error(f"Groq erreur HTTP {e.response.status_code}: {e.response.text}")
        return jsonify({"transcription": "Erreur transcription"}), 502
    except Exception as e:
        logging.exception("Erreur transcription Groq")
        return jsonify({"transcription": "Impossible de transcrire"}), 502


if __name__ == "__main__":
    print("Professeur Zygomar est prêt ! 🎤")
    print("→ Texte : OpenRouter (amazon/nova-2-lite-v1:free)")
    print("→ Voix → Texte : Groq Whisper (gratuit & ultra rapide)")
    app.run(host="0.0.0.0", port=8000, debug=True)