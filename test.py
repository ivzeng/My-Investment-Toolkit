import tkinter as tk
from tkinter import messagebox as mb
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from pygame import mixer



import tkinter as tk

import tkinter as tk
root = tk.Tk()

# Example widgets
widget1 = tk.Label(root, text="X")
widget2 = tk.Label(root, text="X")
widget3 = tk.Label(root, text="X")
widget4 = tk.Label(root, text="X")
widget5 = tk.Label(root, text="X")
widget6 = tk.Label(root, text="X")
widgetT = tk.Label(root, text="T")
widgetB = tk.Label(root, text="B")

# Placing widgets in the grid
widget1.grid(row=0, column=0, sticky="W")
widget2.grid(row=0, column=1, sticky="W")
widget3.grid(row=0, column=2, sticky="W")
widget4.grid(row=1, column=0, sticky="W")
widget5.grid(row=1, column=1, sticky="W")
widget6.grid(row=1, column=2, sticky="W")
widgetT.grid(row=2, column=0, columnspan=4, sticky="W")
widgetB.grid(row=2, column=4, sticky="W")

# Configure column weights to ensure proper spacing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)

root.mainloop()
