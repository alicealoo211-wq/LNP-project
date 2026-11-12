"""
STEP 2 - Make the circle move (animation loop).

New ideas in this step:
  * An animation is just: erase -> update positions -> redraw, many times a second.
  * root.after(16, tick) asks tkinter to call tick() again in 16 milliseconds
    (about 60 times per second). tick() schedules itself, so it repeats forever.
  * We never use a `while True:` loop - that would freeze the window, because
    tkinter needs mainloop() free to handle the mouse and keyboard.

The circle (our LNP) falls toward a line (the cell membrane) and stops on it.

Run:  python learn/step2_animation.py
"""

import tkinter as tk

root = tk.Tk()
root.title("Step 2 - animation loop")
canvas = tk.Canvas(root, width=800, height=600, bg="#0a0e1a")
canvas.pack()

# The "state" of our tiny world: everything that changes over time
lnp_y = 50          # vertical position of the LNP (pixels from the top)
speed = 2           # pixels it moves per frame
MEMBRANE_Y = 450    # where the membrane is
RADIUS = 40


def tick():
    global lnp_y

    # 1. UPDATE: move the LNP down until it touches the membrane
    if lnp_y + RADIUS < MEMBRANE_Y:
        lnp_y += speed

    # 2. ERASE everything from the previous frame
    canvas.delete("all")

    # 3. DRAW the new frame
    canvas.create_line(0, MEMBRANE_Y, 800, MEMBRANE_Y, fill="#deb887", width=6)
    canvas.create_text(120, MEMBRANE_Y + 20, text="cell membrane", fill="#deb887")
    canvas.create_oval(400 - RADIUS, lnp_y - RADIUS, 400 + RADIUS, lnp_y + RADIUS,
                       fill="#6e8ce6", outline="white")
    canvas.create_text(400, 30, text=f"LNP y = {lnp_y}", fill="white")

    # 4. SCHEDULE the next frame
    root.after(16, tick)


tick()          # start the loop once; it keeps itself going after that
root.mainloop()
