import pyautogui
from auto_messenger import image_search

screenWidth, screenHeight = pyautogui.size()
#currentMouseX, currentMouseY = pyautogui.position()

#search_bar_coordinates = image_search.find_search_bar()

search_bar_coordinates = (848, 99)

pyautogui.moveTo(*search_bar_coordinates)

pyautogui.click()
pyautogui.click()
pyautogui.typewrite('Santiago', interval=0.25)  # type with quarter-second pause in between each key

contact_y_delta = 120
contact_coordinates = search_bar_coordinates[0], search_bar_coordinates[1] + contact_y_delta
pyautogui.moveTo(*contact_coordinates)
pyautogui.click()

#chat_bar_coordinates = image_search.find_chat()
#pyautogui.moveTo(*contact_coordinates)
#pyautogui.click()

pyautogui.typewrite('Test message sent automatically', interval=0.25)
pyautogui.press('enter')



"""
pyautogui.moveRel(None, 10)  # move mouse 10 pixels down
pyautogui.doubleClick()
pyautogui.moveTo(500, 500, duration=2, tween=pyautogui.easeInOutQuad)  # use tweening/easing function to move mouse over 2 seconds.
pyautogui.typewrite('Hello world!', interval=0.25)  # type with quarter-second pause in between each key
pyautogui.press('esc')
pyautogui.keyDown('shift')
pyautogui.press(['left', 'left', 'left', 'left', 'left', 'left'])
pyautogui.keyUp('shift')
pyautogui.hotkey('ctrl', 'c')
"""
