import tkinter as tk
from tkinter import messagebox as mb
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from pygame import mixer




def trigger_notice():
    mixer.init()
    sound = mixer.Sound('sound/alarm2.mp3')
    sound.play()
    mb.showinfo('Notice', 'Trade point triggered!')
    sound.fadeout(2000)
    time.sleep(2)


trigger_notice()