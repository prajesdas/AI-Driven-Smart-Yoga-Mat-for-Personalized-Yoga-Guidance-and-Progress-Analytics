from assistant_utils import speak1
import time

def burpees():
    speak1("Start burpees. Do 10 repetitions.")
    for i in range(1, 11):
        speak1(f"Burpee {i}")
        time.sleep(3)
    speak1("Great job! You completed burpees.")

if __name__ == "__main__":
    burpees()
