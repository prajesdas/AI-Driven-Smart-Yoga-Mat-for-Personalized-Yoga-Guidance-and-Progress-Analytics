from assistant_utils import speak1
import time

def sit_ups():
    speak1("Let's do sit-ups. Perform 15 repetitions.")
    for i in range(1, 16):
        speak1(f"Sit-up {i}")
        time.sleep(2)
    speak1("Good job! You completed sit-ups.")

if __name__ == "__main__":
    sit_ups()
