import antigravity
import time
coffee = "coffee"
print("Buckle up, we're taking off!")#Created by Aryan 
antigravity.fly()
print(f"\nLooks like we're out of fuel. Time to refuel with some {coffee}.\n")
while True:
    code = input("Enter your code here: ")
    try:
        exec(code)
    except Exception as e:
        print(f"Looks like we've got a {type(e).__name__} error. Time to take a break and refuel with some {coffee}!")
        time.sleep(10)  # Pause for effect
        print("Feeling better? Let's get back to coding!")
    else:
        print("Nice work! Time to reward yourself with a fresh cup of coffee.")

print("Code, coffee, antigravity, repeat!")
