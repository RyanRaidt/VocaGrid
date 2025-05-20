import pyautogui
import time

# Disable failsafe in case you move mouse to top-left by accident
pyautogui.FAILSAFE = False

def move_to_grid_cell(col_letter: str, row_number: int, screen_width: int, screen_height: int, columns=20, rows=20):
    """
    Convert grid cell like 'C9' to screen coordinates and move the mouse.
    Accepts dynamic grid size (columns x rows).
    """
    col_index = ord(col_letter.upper()) - 65  # A = 0
    row_index = row_number - 1                # 1 = 0

    cell_width = screen_width / columns
    cell_height = screen_height / rows

    target_x = int(col_index * cell_width + cell_width / 2)
    target_y = int(row_index * cell_height + cell_height / 2)

    print(f"📍 Moving to cell {col_letter.upper()}{row_number}")
    print(f"→ Grid size: {columns}×{rows}")
    print(f"→ Screen size: {screen_width}x{screen_height}")
    print(f"→ Cell size: {round(cell_width)}x{round(cell_height)}")
    print(f"→ Target pixel: ({target_x}, {target_y})")

    time.sleep(0.2)  # Slight buffer to avoid overlay interference
    pyautogui.moveTo(target_x, target_y)

def click(action: str):
    """
    Perform a mouse click based on the action string.
    """
    print(f"🖱️ Executing click action: {action}")
    time.sleep(0.3)  # Delay to give movement time to finish

    if action == "left_click":
        pyautogui.click()
    elif action == "right_click":
        pyautogui.rightClick()
    elif action == "double_click":
        pyautogui.doubleClick()
    else:
        print("❌ Unknown click command.")
