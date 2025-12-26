import io
import os
import speech_recognition as sr
from flask import Flask, render_template
from flask_socketio import SocketIO
from pydub import AudioSegment
import google.generativeai as genai

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

recognizer = sr.Recognizer()
audio_buffer = b""

# ---------- GEMINI SETUP ----------
genai.configure(api_key=os.getenv("AIzaSyDpBzpowZAKdtdhU-BwM1iu8pLm7NovKmI"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------- USER PROFILE ----------
user_profile = {
    "age": None,
    "weight": None,
    "gender": None,
    "fitness_level": None,
    "goal": None,
    "past_performance": None
}

@app.route("/")
def index():
    return render_template("index.html")

# ---------- SOCKET AUDIO ----------
@socketio.on("audio_chunk")
def receive_audio(data):
    global audio_buffer
    audio_buffer += data

    if len(audio_buffer) > 16000 * 5:
        process_audio(audio_buffer)
        audio_buffer = b""

# ---------- GEMINI PLAN ----------
def generate_yoga_plan(profile):
    prompt = f"""
Generate a personalized yoga plan in TABLE format only.

User Details:
Age: {profile['age']}
Weight: {profile['weight']}
Gender: {profile['gender']}
Fitness Level: {profile['fitness_level']}
Past Performance: {profile['past_performance']}
Goal: {profile['goal']}

Table format:
Day | Focus | Yoga Poses | Reps/Duration | Benefit
"""

    response = model.generate_content(prompt)
    return response.text

# ---------- AUDIO PROCESS ----------
def process_audio(webm_bytes):
    try:
        audio = AudioSegment.from_file(io.BytesIO(webm_bytes), format="webm")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data).lower()

            # ---------- PROFILE CAPTURE ----------
            if "age is" in text:
                user_profile["age"] = int("".join(filter(str.isdigit, text)))
                socketio.emit("model_output", {"text": "Age recorded"})
                return

            if "weight is" in text:
                user_profile["weight"] = int("".join(filter(str.isdigit, text)))
                socketio.emit("model_output", {"text": "Weight recorded"})
                return

            if "gender" in text:
                if "male" in text:
                    user_profile["gender"] = "male"
                elif "female" in text:
                    user_profile["gender"] = "female"
                socketio.emit("model_output", {"text": "Gender recorded"})
                return

            if "fitness level" in text:
                user_profile["fitness_level"] = text.replace("fitness level", "").strip()
                socketio.emit("model_output", {"text": "Fitness level recorded"})
                return

            if "goal" in text:
                user_profile["goal"] = text.replace("goal", "").strip()
                socketio.emit("model_output", {"text": "Goal recorded"})
                return

            if "past performance" in text:
                user_profile["past_performance"] = text.replace("past performance", "").strip()
                socketio.emit("model_output", {"text": "Past performance recorded"})
                return

            # ---------- START EXERCISE ----------
            if "start exercise" in text:
                if None in user_profile.values():
                    socketio.emit("model_output", {
                        "text": "Please provide all details first"
                    })
                else:
                    plan = generate_yoga_plan(user_profile)
                    socketio.emit("model_output", {
                        "text": "Here is your personalized yoga plan",
                        "plan": plan
                    })
                return

            socketio.emit("model_output", {"text": text})

    except Exception as e:
        socketio.emit("model_output", {
            "text": "Sorry, I could not understand."
        })
        print("Error:", e)

# ---------- RUN ----------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
