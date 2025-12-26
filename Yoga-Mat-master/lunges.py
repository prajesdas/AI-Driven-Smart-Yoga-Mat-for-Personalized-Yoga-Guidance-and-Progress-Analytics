from assistant_utils import speak1
import time

def lunges():
    speak1("Let's do lunges. Perform 10 repetitions per leg.")
    for i in range(1, 11):
        speak1(f"Lunge {i} left leg")
        time.sleep(2)
        speak1(f"Lunge {i} right leg")
        time.sleep(2)
    speak1("Well done! You completed the lunges.")

if __name__ == "__main__":
    lunges()
