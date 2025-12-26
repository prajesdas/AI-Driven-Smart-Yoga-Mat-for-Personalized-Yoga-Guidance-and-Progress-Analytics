import requests
import json
import pyttsx3

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 170)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def latestnews():
    api_dict = {
        "business": "YOUR_BUSINESS_API_URL",
        "entertainment": "YOUR_ENTERTAINMENT_API_URL",
        "health": "YOUR_HEALTH_API_URL",
        "science": "YOUR_SCIENCE_API_URL",
        "sports": "YOUR_SPORTS_API_URL",
        "technology": "YOUR_TECHNOLOGY_API_URL"
    }

    speak("Which field news do you want? Business, Health, Technology, Sports, Entertainment, or Science?")
    field = input("Enter the news category: ").strip().lower()

    url = api_dict.get(field)
    if not url:
        print("Invalid category or URL not found.")
        speak("Invalid category. Please try again.")
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()

        if "articles" not in news_data or not news_data["articles"]:
            speak("No news available at the moment.")
            return

        speak("Here is the first news.")

        for article in news_data["articles"]:
            title = article["title"]
            print(title)
            speak(title)

            news_url = article.get("url", "No URL provided")
            print(f"For more info, visit: {news_url}")

            user_input = input("[Press 1 to continue, 2 to stop]: ")
            if user_input == "2":
                break
        
        speak("That's all for now.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        speak("Unable to fetch news at the moment.")

if __name__ == "__main__":
    latestnews()
