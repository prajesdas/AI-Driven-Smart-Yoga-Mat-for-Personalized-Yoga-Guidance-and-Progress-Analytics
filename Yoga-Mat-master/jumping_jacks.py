from assistant_utils import speak1
import time

def jumping_jacks():
    speak1("Start jumping jacks. Do 20 repetitions.")
    for i in range(1, 21):
        speak1(f"Jumping jack {i}")
        time.sleep(1)
    speak1("Good job! You completed jumping jacks.")

if __name__ == "__main__":
    jumping_jacks()
