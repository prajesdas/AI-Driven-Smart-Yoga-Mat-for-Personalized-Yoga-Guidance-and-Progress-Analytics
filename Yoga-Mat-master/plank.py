from assistant_utils import speak1
import time

def plank():
    speak1("Hold the plank position for 30 seconds.")
    time.sleep(30)
    speak1("Great! You completed the plank.")

if __name__ == "__main__":
    plank()
