import time
import webbrowser
import pyttsx3
import speech_recognition
import os
import pyautogui
from plyer import notification
import threading
import cv2  
import mediapipe as md  
import math  
import wandb
from google import genai

# Setup Gemini Client
client = genai.Client(api_key="AIzaSyChOLNEUQnagCRx5_SkFEkKLMIklEw7-hI")

# Initialize W&B Project
wandb.init(project="Yoga-Mat-Assistant", entity="shreyashtiwari-narula-institute-of-technology")

engine1 = pyttsx3.init("sapi5")
voices1 = engine1.getProperty("voices")
engine1.setProperty("voice", voices1[0].id)
engine1.setProperty("rate", 170)

def speak1(audio):
    engine1.say(audio)
    engine1.runAndWait()

def takeCommand1():
    r1 = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Listening.....Speak now ")
        r1.pause_threshold = 1
        r1.energy_threshold = 300
        audio = r1.listen(source, 0, 4)
    try:
        print("Understanding..")
        query1 = r1.recognize_google(audio, language='en-in')
        print(f"You Said: {query1}\n")
    except Exception as e:
        speak1("Say that again please ")
        print("Say that again please ")
        return "None"
    return query1

def water_reminder():
    while True:
        time.sleep(300) 
        notification.notify(
            title="Stay Hydrated!",
            message="It's time to drink some water! Stay hydrated for better performance.",
            app_name="Yoga Mat Assistant",
            timeout=10
        )

water_thread = threading.Thread(target=water_reminder, daemon=True)
water_thread.start()

for i in range(10):
    speak1("Enter the password to open the Yoga Mat Assistant")
    a = input("Enter Password: ").strip().lower()
    try:
        pw_file = open("password.txt", "r")
        pw = pw_file.read().strip().lower()
        pw_file.close()
    except FileNotFoundError:
        pw = "admin" 
        
    if a == pw:
        speak1("WELCOME SIR! PLEASE SPEAK [WAKE UP] TO LOAD ME UP")
        print("WELCOME SIR! PLEASE SPEAK [WAKE UP] TO LOAD ME UP")
        break
    elif i == 2:
        exit()
    else:
        print("Wrong password! Retry")

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
rate = engine.setProperty("rate", 170)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        print("Listening.....")
        r.pause_threshold = 1
        r.energy_threshold = 300
        audio = r.listen(source, 0, 4)
    try:
        print("Understanding..")
        query = r.recognize_google(audio, language='en-in')
        print(f"You Said: {query}\n")
    except Exception:
        print("Say that again")
        return "None"
    return query

user_details = {
    "age": None,
    "height": None,
    "weight": None,
    "gender": None
}

def start_exercise():
    def get_voice_input(prompt):
        for _ in range(4):
            speak1(prompt)
            response = takeCommand().strip().lower()
            if response and response != "none":
                print(f"Captured input: {response}")
                return response
            speak1("I didn't catch that. Please say it again.")
        speak1("Too many failed attempts. Please try again later.")
        return None
    age = get_voice_input("Please say your age.")
    if not age:
        return None
    height = get_voice_input("Now, say your height in centimeters.")
    if not height:
        return None
    weight = get_voice_input("Say your weight in kilograms.")
    if not weight:
        return None
    speak1("Enter your gender now")
    gender = input("Enter your gender (Male/Female): ").strip().lower()
    while gender not in ["male", "female"]:
        print("Invalid input. Please enter 'Male' or 'Female'.")
        gender = input("Enter your gender (Male/Female): ").strip().lower()
    user_details["age"] = age
    user_details["height"] = height
    user_details["weight"] = weight
    user_details["gender"] = gender
    speak1(f"Your details have been recorded: Age {age}, Height {height} cm, Weight {weight} kg, Gender {gender}.")
    speak1("What workout do you want to perform.")
    return age, height, weight, gender

def get_pushup_goal(age, weight, gender):
    age = int(age)
    weight = int(weight)
    if gender == "female":
        if 18 <= age <= 29:
            if weight < 70: return "44 or more", "Excellent"
            elif 70 <= weight <= 90: return "40 or more", "Excellent"
            else: return "35 or more", "Excellent"
        elif 30 <= age <= 39:
            if weight < 70: return "40 or more", "Excellent"
            elif 70 <= weight <= 90: return "35 or more", "Excellent"
            else: return "30 or more", "Excellent"
    elif gender == "male":
        if 18 <= age <= 29:
            if weight < 60: return "24 or more", "Excellent"
            elif 60 <= weight <= 75: return "20 or more", "Excellent"
            else: return "15 or more", "Excellent"
        elif 30 <= age <= 39:
            if weight < 60: return "20 or more", "Excellent"
            elif 60 <= weight <= 75: return "18 or more", "Excellent"
            else: return "10 or more", "Excellent"
    return "10", "Average"

def pushups():
    count = 0
    last_gemini_time = 0 # Track time for rate limiting
    
    age = user_details.get("age")
    weight = user_details.get("weight")
    gender = user_details.get("gender")

    if not all([age, weight, gender]):
        speak("Please provide your details first by saying 'start exercise'.")
        return

    pushup_goal, category = get_pushup_goal(age, weight, gender)
    speak(f"Based on your age, weight, and gender, you should aim for {pushup_goal} push-ups to achieve an {category} rating.")
    speak("Starting push-ups, get ready!")
    speak("The body should form a straight line from head to heels throughout the entire movement. The elbows should ideally be at approximately a 45-degree angle to the body, not flared out too wide.")
    
    md_drawing = md.solutions.drawing_utils
    md_pose = md.solutions.pose
    position = None
    cap = cv2.VideoCapture(0)

    def calculate_angle(a, b, c):
        radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
        angle = math.degrees(radians)
        angle = abs(angle)
        if angle > 180.0:
            angle = 360 - angle
        return angle

    def smooth_angle(angle, previous_angle, alpha=0.2):
        if previous_angle is None:
            return angle
        return alpha * angle + (1 - alpha) * previous_angle

    left_elbow_angle_smoothed = None
    right_elbow_angle_smoothed = None

    with md_pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            imlist = []
            
            if result.pose_landmarks:
                md_drawing.draw_landmarks(image, result.pose_landmarks, md_pose.POSE_CONNECTIONS)
                for id, im in enumerate(result.pose_landmarks.landmark):
                    h, w, _ = image.shape
                    X, Y = int(im.x * w), int(im.y * h)
                    imlist.append([id, X, Y])
            
            if len(imlist) > 24: 
                # GEMINI RATE LIMIT FIX: Use time instead of frames
                current_time = time.time()
                if current_time - last_gemini_time > 15: # Wait 15 seconds between calls
                    coord_data = f"Shoulders: L({imlist[11][1:]}), R({imlist[12][1:]}) Hips: L({imlist[23][1:]}), R({imlist[24][1:]})"
                    prompt = f"Analyze these yoga coordinates: {coord_data}. Is the user leaning? Answer in 5 words."
                    try:
                        print("DEBUG: Requesting Gemini Analysis...")
                        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                        print(f"DEBUG: Gemini Response: {response.text}")
                        speak(response.text) 
                        last_gemini_time = current_time # Update time only on request
                    except Exception as e:
                        print(f"DEBUG: Gemini Error: {e}")
                        last_gemini_time = current_time # Update time to avoid spamming on errors

                left_elbow_angle = calculate_angle(imlist[11][1:], imlist[13][1:], imlist[15][1:])
                right_elbow_angle = calculate_angle(imlist[12][1:], imlist[14][1:], imlist[16][1:])
                left_elbow_angle_smoothed = smooth_angle(left_elbow_angle, left_elbow_angle_smoothed)
                right_elbow_angle_smoothed = smooth_angle(right_elbow_angle, right_elbow_angle_smoothed)
                
                elbows_bent = (left_elbow_angle_smoothed <= 55 or right_elbow_angle_smoothed <= 55)
                hip_buffer = 10
                hips_low = (imlist[12][2] >= (imlist[14][2] + hip_buffer) and imlist[11][2] >= (imlist[13][2] + hip_buffer))
                chest_down = (imlist[11][2] >= imlist[0][2] + 20 or imlist[12][2] >= imlist[0][2] + 20)
                
                if hips_low and elbows_bent and chest_down:
                    if position != "down":
                        position = "down"
                elif hips_low and not elbows_bent:
                    cv2.putText(image, "Bend elbows more!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif not hips_low and elbows_bent:
                    cv2.putText(image, "Lower your chest more!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    position = None
                
                if position == "down" and not elbows_bent:
                    position = "up"
                    count += 1
                    print(count)
            
            cv2.putText(image, f"Count: {count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.imshow("Push-up counter", image)
            key = cv2.waitKey(1)
            if key == ord('q') or count >= int(pushup_goal.split()[0]):
                break

    cap.release()
    cv2.destroyAllWindows()
    
    wandb.log({"total_pushups": count, "age": age, "weight": weight})
    
    try:
        feedback_prompt = f"The user completed {count} pushups. Give 1 sentence of praise."
        response = client.models.generate_content(model="gemini-2.0-flash", contents=feedback_prompt)
        speak(response.text)
    except Exception as e:
        speak("Great job! You have completed your push-ups.")

if __name__ == "__main__":
    while True:
        query = takeCommand().lower()
        if "wake up" in query:
            try:
                from GreetMe import greetMe
                greetMe()
            except ImportError:
                speak("I am awake and ready, sir.")
                
            while True:
                query = takeCommand().lower()
                if "go to sleep" in query:
                    speak("Ok sir, You can call me anytime")
                    break
                elif "start exercise" in query:
                    details = start_exercise()
                    if details:
                        age, height, weight, gender = details
                elif "push up" in query:
                    pushups()
                elif "sit ups" in query:
                    os.system("python situps.py")
                elif "squats" in query:
                    os.system("python squats.py")             
                elif "hello" in query:
                    speak("Hello sir, how are you?")
                elif "i am fine" in query:
                    speak("That's great, sir")
                elif "how are you" in query:
                    speak("Perfect, sir")
                elif "thank you" in query:
                    speak("You are welcome, sir")
                elif "tired" in query:
                    speak("Playing your favourite songs, sir")
                    webbrowser.open("https://youtu.be/2g5xkLqIElU")
                elif "pause" in query:
                    pyautogui.press("k")
                    speak("Video paused")
                elif "play" in query:
                    pyautogui.press("k")
                    speak("Video played")
                elif "mute" in query:
                    pyautogui.press("m")
                    speak("Video muted")
                elif "volume up" in query:
                    try:
                        from keyboard import volumeup
                        speak("Turning volume up, sir")
                        volumeup()
                    except ImportError: speak("Keyboard module not found.")
                elif "volume down" in query:
                    try:
                        from keyboard import volumedown
                        speak("Turning volume down, sir")
                        volumedown()
                    except ImportError: speak("Keyboard module not found.")
                elif "finally sleep" in query:
                    speak("Going to sleep, sir")
                    exit()