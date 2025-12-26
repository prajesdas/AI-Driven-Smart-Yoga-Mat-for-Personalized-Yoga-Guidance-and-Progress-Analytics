from assistant_utils import speak1
import time

def high_knees():
    speak1("Start high knees. Do 20 repetitions.")
    for i in range(1, 21):
        speak1(f"High knee {i}")
        time.sleep(1)
    speak1("Good job! You completed high knees.")

if __name__ == "__main__":
    high_knees()
