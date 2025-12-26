from assistant_utils import speak1
import time

def yoga_warrior_pose():
    speak1("Hold the Warrior Pose for 30 seconds on each side.")
    time.sleep(30)
    speak1("Switch sides.")
    time.sleep(30)
    speak1("Great! You completed the Warrior Pose.")

if __name__ == "__main__":
    yoga_warrior_pose()
