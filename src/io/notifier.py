import tkinter as tk
from tkinter import messagebox as mb
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from pygame import mixer
import time



notifier_set = {
    'BaseNotifier',
    'MessageboxNotifier'}


class BaseNotifier:
    def __init__(self) -> None:
        pass
    
    def notify(self, message, *_):
        pass


class MessageboxNotifier(BaseNotifier):
    def __init__(self) -> None:
        return

    def notify(self, message, *_):
        mixer.init()
        sound = mixer.Sound('sound/alarm2.mp3')
        sound.play()
        mb.showinfo('Notice:', message)
        sound.fadeout(2000)
        time.sleep(2)

