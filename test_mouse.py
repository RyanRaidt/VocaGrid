import pyautogui
import time

pyautogui.FAILSAFE = False

print("Moving mouse in 3 seconds...")
time.sleep(3)
pyautogui.moveTo(500, 500)
print("Clicking in 2 seconds...")
time.sleep(2)
pyautogui.click()
