from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from threading import Thread
from pynput import keyboard
import time
import sys      
import PySimpleGUI as sg

sys.tracebacklimit = 0


class MyException(Exception): pass
class TimeException(Exception): pass
class WordsException(Exception): pass
def on_press(key):
    global current_word
    global timer
    if timer == "0:00":
        raise TimeException(time)
    if current_word == len(word_list):
        raise WordsException(current_word)
    if key == keyboard.Key.esc:
        raise MyException(key)
    timer = wait.until(EC.presence_of_element_located((By.ID, "timer")))
    inputElement.send_keys(word_list[current_word]+" ")
    current_word += 1
    
def FullSpeed():
    driver = webdriver.Firefox(executable_path=r'/home/whadri/geckodriver')
    driver.get("http://10fastfingers.com/typing-test/english")
    wait = WebDriverWait(driver, 10)
    inputElement = wait.until(EC.presence_of_element_located((By.ID, "inputfield")))
    time.sleep(4)
    word_list = driver.execute_script("return words")
    for word in word_list:
        inputElement.send_keys(word+" ")

def ControlledSpeed(score_wanted):
    driver = webdriver.Firefox(executable_path=r'/home/whadri/geckodriver')
    driver.get("http://10fastfingers.com/typing-test/english")
    wait = WebDriverWait(driver, 10)
    inputElement = wait.until(EC.presence_of_element_located((By.ID, "inputfield")))
    time.sleep(4)
    word_list = driver.execute_script("return words")
    time_sleep = 60/score_wanted
    for word in word_list:
        timer = wait.until(EC.presence_of_element_located((By.ID, "timer")))
        inputElement.send_keys(word+" ")
        time.sleep(time_sleep)
        if timer.text == '0:00':
            break

def typingWindow():
    layout_type_in = [[sg.Multiline('')]]
    window_type_in = sg.Window('Speed Choice', layout_type_in, size=(750,700))
    while True:
        events_type, value_type = window_type_in.read()
        if events_type == sg.WINDOW_CLOSED:
            break
    window_type_in.close()


def KeyStrokeSpeed():
    global timer, current_word, word_list, wait, inputElement
    driver = webdriver.Firefox(executable_path=r'/home/whadri/geckodriver')
    driver.get("http://10fastfingers.com/typing-test/english")
    wait = WebDriverWait(driver, 10)
    inputElement = wait.until(EC.presence_of_element_located((By.ID, "inputfield")))
    time.sleep(4)
    word_list = driver.execute_script("return words")
    timer = wait.until(EC.presence_of_element_located((By.ID, "timer")))
    current_word = 0
    with keyboard.Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except MyException as e:
            print('{0} was pressed'.format(e.args[0]))
            driver.close()
        except TimeException as e:
            print('timeout')
        except WordsException as e:
            print("All words are written")

def execute():
    timer = 0
    current_word = 0
    word_list = []
    wait = None
    inputElement = None
    A = [sg.Button(button_text="mode 0"), sg.Button(button_text="mode 1"), sg.Button(button_text="mode 2")]
    # Define the window's contents
    layout_main = [[sg.Text(text = "Welcome to the 10fastfingers hack", text_color='blue', background_color="white", justification='center', pad=(2500/10,20/20))],
              [sg.Text()],
              [sg.Text(text = "Choose your mode by clicking on one of the three choices", text_color='blue', justification='center', pad=(1200/10,10000/10000))],
              [sg.Text()],
              [sg.Text()],
              [sg.Button('Full speed',key='-mode0-', tooltip="Sending all words at a time"), sg.Button("Controlled speed",key='-mode1-', tooltip = "Choose speed"), 
               sg.Button("Keystroke speed",key='-mode2-', tooltip="Keystroke")],
              [sg.Text(size=(40,1), key='-OUTPUT-')],
              [sg.Text("",size=(40,1), key="-speed-")]]

    layout_slider = [[sg.Slider(range=(1,340),
             default_value=60,
             size=(20,15),
             orientation='horizontal',
             font=('Helvetica', 12),
                         key='Slider',
                         enable_events=True)]]
    
    # Create the window
    window = sg.Window('10fastfingers Speed typer', layout_main, size=(750,200), grab_anywhere=True, element_justification='c')
    # Display and interact with the Window using an Event Loop
    while True:
        event, values = window.read()
        if event == '-mode0-':
            try:
                FullSpeed()
            except:
                pass
        if event == '-mode1-':
            window_slider = sg.Window('Speed Choice', layout_slider)
            while True:
                events_slider, values_slider = window_slider.read()

                if events_slider == sg.WINDOW_CLOSED:
                    break
                else:
                    score_wanted = values_slider[events_slider]
            window_slider.close()
            window['-speed-'].update(f'Your speed on mode <<Controlled speed>> is:{score_wanted}')
            try:
                ControlledSpeed(score_wanted)
            except:
                pass
        if event == '-mode2-':
            try:
                Thread(target = typingWindow).start()
                Thread(target = KeyStrokeSpeed).start()
            except:
                pass
        if event == sg.WINDOW_CLOSED:
            break


    # Finish up by removing from the screen
    window.close()
if __name__ == "__main__":
    execute()