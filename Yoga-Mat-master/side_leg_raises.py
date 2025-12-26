from assistant_utils import speak1
import time

def side_leg_raises():
    speak1("Lie on your side and do 10 leg raises on each side.")
    for i in range(1, 11):
        speak1(f"Leg raise {i} on left side")
        time.sleep(2)
    for i in range(1, 11):
        speak1(f"Leg raise {i} on right side")
        time.sleep(2)
    speak1("Well done! You completed side leg raises.")

if __name__ == "__main__":
    side_leg_raises()
