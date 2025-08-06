import os
import json
import requests
import tempfile
import speech_recognition as sr
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from elevenlabs.client import ElevenLabs
import threading
import time

# Load environment variables
load_dotenv()

# Load API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

if not ELEVEN_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY not found in .env")

# ElevenLabs client setup
client = ElevenLabs(api_key=ELEVEN_API_KEY)

# Available voices with their IDs
AVAILABLE_VOICES = {
    "aria": {"id": "pFZP5JQG7iQjIQuC4Bku", "name": "Aria (Female, Professional)"},
    "rachel": {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel (Female, Calm)"},
    "adam": {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam (Male, Professional)"},
    "josh": {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh (Male, Friendly)"},
    "arnold": {"id": "VR6AewLTigWG4xSOukaG", "name": "Arnold (Male, Deep)"},
    "bella": {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella (Female, Warm)"},
    "elli": {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli (Female, Young)"},
    "james": {"id": "ZQe5CZNOzWyzPSCn5a3c", "name": "James (Male, Mature)"}
}

# Speech recognition setup
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Load patient records
def load_patient_data():
    try:
        with open(r"C:\Users\ABHAYEYSVS\Desktop\speech_bot\product_3\data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: data.json not found. Using sample data.")
        return {
            "patients": [
                {
                    "name": "John Smith",
                    "phone": "555-0123",
                    "date_of_birth": "1985-06-15",
                    "appointment_date": "2024-02-15",
                    "appointment_time": "10:30 AM"
                },
                {
                    "name": "Jane Doe",
                    "phone": "555-0456",
                    "date_of_birth": "1990-03-22",
                    "appointment_date": "2024-02-16",
                    "appointment_time": "2:00 PM"
                },
                {
                    "name": "Alice Johnson",
                    "phone": "555-0789",
                    "date_of_birth": "1988-11-10",
                    "appointment_date": "2024-02-17",
                    "appointment_time": "9:00 AM"
                },
                {
                    "name": "Bob Wilson",
                    "phone": "555-0321",
                    "date_of_birth": "1992-07-25",
                    "appointment_date": "2024-02-18",
                    "appointment_time": "3:30 PM"
                }
            ]
        }

patients = load_patient_data()

# System prompt template
system_prompt = f"""
You are a friendly medical receptionist handling patient verification calls.
Your responses will be converted to speech, so keep them natural and conversational.

Available patient records:
{json.dumps(patients, indent=2)}

Your role:
1. Greet the caller warmly
2. Ask for patient details one by one (name, phone, date of birth)
3. After collecting all details, verify against the patient records
4. Respond with either "Patient verified - your appointment details are confirmed!" or "Sorry, I cannot find a patient with those details in our system"

Speech-optimized guidelines:
- Keep responses conversational and natural for speech
- Use clear, simple language that's easy to understand when spoken
- Ask one question at a time and wait for responses
- Be patient and understanding as users may be using voice input
- Keep responses under 30 words for better voice interaction

Important: Only verify a patient after you have collected ALL three pieces of information: name, phone number, and date of birth.
"""

# Call Groq API
def call_groq_api(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error calling API: {str(e)}"

# Validate patient info
def validate_patient_info(name, phone, dob):
    name_lower = name.lower().strip()
    phone_clean = phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")

    for patient in patients["patients"]:
        if (patient["name"].lower() == name_lower and 
            patient["phone"].replace("-", "") == phone_clean and 
            patient["date_of_birth"] == dob):
            return True, patient

    return False, None

# AI receptionist conversation flow
def chat_with_receptionist(user_message, history=None):
    if history is None or len(history) == 0:
        history = [{"role": "system", "content": system_prompt}]
        ai_response = "Hello! Welcome to our medical office. I'm here to help verify your patient information. Could you please tell me your full name?"
        history.append({"role": "assistant", "content": ai_response})
    else:
        history.append({"role": "user", "content": user_message})
        ai_response = call_groq_api(history)
        history.append({"role": "assistant", "content": ai_response})

    return history, ai_response

# Enhanced TTS with voice selection
def text_to_speech(text, voice_id="pFZP5JQG7iQjIQuC4Bku", filename="output.mp3"):
    try:
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        audio_bytes = b"".join(audio)
        with open(filename, "wb") as f:
            f.write(audio_bytes)
        return filename
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        return None

# Speech to text function
def speech_to_text():
    try:
        with microphone as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        return text
    except sr.WaitTimeoutError:
        return "Sorry, I didn't hear anything. Please try again."
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand what you said. Please try again."
    except sr.RequestError as e:
        return f"Sorry, there was an error with the speech recognition service: {e}"

# Flask setup
app = Flask(__name__)
CORS(app)
chat_sessions = {}

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/voices", methods=["GET"])
def get_voices():
    return jsonify({"voices": AVAILABLE_VOICES})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_input = data.get("message", "")
        session_id = data.get("session_id", "default")
        voice_id = data.get("voice_id", "pFZP5JQG7iQjIQuC4Bku")

        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        chat_history = chat_sessions[session_id]
        chat_history, response = chat_with_receptionist(user_input, chat_history)
        chat_sessions[session_id] = chat_history

        # Generate speech with selected voice
        audio_path = text_to_speech(response, voice_id)

        return jsonify({
            "response": response,
            "session_id": session_id,
            "message_count": len(chat_history),
            "speech_enabled": True,
            "audio_available": audio_path is not None
        })

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/voice_chat", methods=["POST"])
def voice_chat():
    try:
        data = request.get_json()
        session_id = data.get("session_id", "default")
        voice_id = data.get("voice_id", "pFZP5JQG7iQjIQuC4Bku")

        # Get speech input
        user_input = speech_to_text()
        
        if "Sorry" in user_input and ("didn't hear" in user_input or "couldn't understand" in user_input):
            return jsonify({
                "error": user_input,
                "session_id": session_id,
                "speech_enabled": True
            })

        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        chat_history = chat_sessions[session_id]
        chat_history, response = chat_with_receptionist(user_input, chat_history)
        chat_sessions[session_id] = chat_history

        # Generate speech response
        audio_path = text_to_speech(response, voice_id)

        return jsonify({
            "user_input": user_input,
            "response": response,
            "session_id": session_id,
            "message_count": len(chat_history),
            "speech_enabled": True,
            "audio_available": audio_path is not None
        })

    except Exception as e:
        return jsonify({"error": f"Voice chat error: {str(e)}"}), 500

@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json()
        text = data.get("text", "")
        voice_id = data.get("voice_id", "pFZP5JQG7iQjIQuC4Bku")
        
        if not text:
            return jsonify({"error": "No text provided"}), 400

        filename = text_to_speech(text, voice_id)
        if filename:
            return send_file(filename, mimetype="audio/mpeg")
        else:
            return jsonify({"error": "Failed to generate audio"}), 500
    except Exception as e:
        return jsonify({"error": f"TTS failed: {str(e)}"}), 500

@app.route("/get_audio", methods=["GET"])
def get_audio():
    try:
        return send_file("output.mp3", mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": f"Audio file not found: {str(e)}"}), 404

@app.route("/reset", methods=["POST"])
def reset():
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id", "default")

        if session_id in chat_sessions:
            del chat_sessions[session_id]

        return jsonify({
            "message": "Chat history reset successfully",
            "session_id": session_id,
            "speech_enabled": True
        })
    except Exception as e:
        return jsonify({"error": f"Error resetting chat: {str(e)}"}), 500

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "healthy",
        "active_sessions": len(chat_sessions),
        "total_messages": sum(len(history) for history in chat_sessions.values()),
        "features": {
            "text_to_speech": True,
            "speech_to_text": True,
            "voice_to_voice": True,
            "multiple_voices": True,
            "auto_speak": True
        },
        "available_voices": len(AVAILABLE_VOICES)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)