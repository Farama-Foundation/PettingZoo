import random
import time
import threading


def inp_handler(name):
    from pynput.keyboard import Key, Controller as KeyboardController

    keyboard = KeyboardController()
    time.sleep(0.1)
    choices = ['w', 'a', 's', 'd', 'j', 'k', Key.left, Key.right, Key.up, Key.down]
    NUM_TESTS = 50
    for x in range(NUM_TESTS):
        i = random.choice(choices) if x != NUM_TESTS - 1 else Key.esc
        keyboard.press(i)
        time.sleep(0.1)
        keyboard.release(i)


def manual_control_test(manual_control):
    manual_in_thread = threading.Thread(target=inp_handler, args=(1,))

    manual_in_thread.start()

    try:
        manual_control()
    except Exception:
        raise Exception("manual_control() has crashed. Please fix it.")

    manual_in_thread.join()
