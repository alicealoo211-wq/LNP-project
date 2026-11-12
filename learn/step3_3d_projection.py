"""
STEP 3 - Fake 3D: rotate points and project them onto the 2D screen.

tkinter can only draw flat (2D) shapes. To show 3D we:
  1. Store every object as points (x, y, z) in a 3D "world".
  2. ROTATE the points by the camera angles (yaw = turn left/right,
     pitch = tilt up/down), using sin and cos.
  3. PROJECT: divide x and y by the depth z. Far points -> smaller numbers ->
     closer to the centre of the screen and drawn smaller. That is perspective.
  4. SORT the points far-to-near and draw the far ones first, so near ones
     cover them (the "painter's algorithm" - like painting a background first).

Here we build a sphere of 120 dots (this is how the LNP is made later).
Drag with the mouse to rotate it.

Run:  python learn/step3_3d_projection.py
"""

import math
import tkinter as tk

W, H = 800, 600
root = tk.Tk()
root.title("Step 3 - 3D projection (drag to rotate)")
canvas = tk.Canvas(root, width=W, height=H, bg="#0a0e1a")
canvas.pack()


def fib_sphere(n):
    """Spread n points evenly over a sphere of radius 1 (the 'Fibonacci sphere').
    y goes evenly from +1 (top) to -1 (bottom); each next point is turned by the
    golden angle (~137.5 degrees) so the points never line up in stripes."""
    points = []
    golden_angle = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n          # height
        r = math.sqrt(1 - y * y)           # radius of the circle at that height
        theta = golden_angle * i           # angle around the vertical axis
        points.append((math.cos(theta) * r, y, math.sin(theta) * r))
    return points


SPHERE = [(x * 2, y * 2, z * 2) for x, y, z in fib_sphere(120)]   # radius 2

# Camera settings
yaw = 0.0        # rotation around the vertical axis (radians)
pitch = 0.3      # tilt (radians)
DIST = 8.0       # how far the camera is from the centre of the world
FOCAL = 500      # zoom of the "lens" (bigger = more zoomed in)


def project(p):
    """3D world point -> (screen x, screen y, depth, scale)."""
    x, y, z = p
    # rotate around the vertical (y) axis by yaw
    x1 = x * math.cos(yaw) - z * math.sin(yaw)
    z1 = x * math.sin(yaw) + z * math.cos(yaw)
    # rotate around the horizontal (x) axis by pitch
    y2 = y * math.cos(pitch) + z1 * math.sin(pitch)
    z2 = -y * math.sin(pitch) + z1 * math.cos(pitch)
    # move the world in front of the camera
    depth = z2 + DIST
    # perspective: divide by depth
    scale = FOCAL / depth
    screen_x = W / 2 + x1 * scale
    screen_y = H / 2 - y2 * scale        # minus, because screen y points DOWN
    return screen_x, screen_y, depth, scale


def draw():
    canvas.delete("all")
    projected = [project(p) for p in SPHERE]
    projected.sort(key=lambda item: -item[2])          # far (big depth) first
    for sx, sy, depth, scale in projected:
        r = 0.2 * scale                                 # ball radius in pixels
        # shade by depth: far dots darker, near dots brighter
        brightness = max(0.25, min(1.0, (DIST + 2 - depth) / 4))
        color = "#%02x%02x%02x" % (int(110 * brightness), int(140 * brightness), int(230 * brightness))
        canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=color, outline="")
    canvas.create_text(W / 2, 30, fill="white", font=("Helvetica", 14),
                       text=f"yaw = {yaw:.2f} rad   pitch = {pitch:.2f} rad   (drag to rotate)")


# --- mouse rotation --------------------------------------------------------
last = [0, 0]


def on_press(e):
    last[0], last[1] = e.x, e.y


def on_drag(e):
    global yaw, pitch
    yaw += (e.x - last[0]) * 0.01
    pitch += (e.y - last[1]) * 0.01
    last[0], last[1] = e.x, e.y


canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", on_drag)


def tick():
    global yaw
    yaw += 0.005           # slow automatic spin
    draw()
    root.after(16, tick)


tick()
root.mainloop()
