"""
STEP 1 - Open a window and draw one circle.

New ideas in this step:
  * tk.Tk()          -> creates the window
  * tk.Canvas(...)   -> a blank drawing surface inside the window
  * create_oval(...) -> draws a circle (an oval inside a box)
  * mainloop()       -> keeps the window open and listening for clicks/keys

Run:  python learn/step1_window.py
"""

import tkinter as tk

# 1. Create the window
root = tk.Tk()
root.title("Step 1 - a window and a circle")

# 2. Put a canvas (drawing area) in it: 800 pixels wide, 600 tall, dark blue
canvas = tk.Canvas(root, width=800, height=600, bg="#0a0e1a")
canvas.pack()

# 3. Draw a circle.
#    create_oval needs the box around the circle: (left, top, right, bottom).
#    Screen coordinates start at the TOP-LEFT corner (0, 0);
#    x grows to the right, y grows DOWNWARD.
center_x, center_y, radius = 400, 300, 60
canvas.create_oval(center_x - radius, center_y - radius,
                   center_x + radius, center_y + radius,
                   fill="#6e8ce6", outline="white")

canvas.create_text(400, 400, text="This circle will become our LNP",
                   fill="white", font=("Helvetica", 16))

# 4. Hand control to tkinter. Nothing after this line runs until the window closes.
root.mainloop()
