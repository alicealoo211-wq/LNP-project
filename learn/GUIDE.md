# In-depth guide: 3D LNP endosomal escape simulation (tkinter)

This guide explains **what the simulation does, how it works, and how it was built step by step**. Use it to understand the code and to explain it to your professor.

- Final program: [`scripts/lnp_endosomal_escape_3d.py`](../scripts/lnp_endosomal_escape_3d.py)
- Practice steps: the `learn/step1 … step6` files in this folder. Each one runs on its own and adds **one** new idea.

> **Be honest about how it was made.** The code was written with the help of an AI assistant (Claude). Tell your professor that, and check your course's AI policy. What matters is that you can explain every part. Working through the steps below is how you get there.

---

## 0. How to run anything here

tkinter comes with Python, so there's nothing to install. In VS Code:

1. Open the file.
2. Bottom-right status bar → pick your Python interpreter (`base` or `lnp`).
3. Press ▶ (Run Python File).

You can also run a file from the VS Code terminal:

```bash
python learn/step1_window.py
```

---

## 1. The big picture

The program is an **animation**. About 30 times per second it:

1. reads the current time `t`,
2. works out where every molecule should be at that time (the **biology**),
3. converts those 3D positions into 2D screen positions (the **3D engine**),
4. draws them as coloured circles.

The final file has four blocks:

| Block | In the final script | Job |
|---|---|---|
| Helper math | `clamp`, `lerp`, `ease`, `add`, `mix`, `fib_sphere` … (lines 16–80) | Small reusable tools |
| The story | `STAGES` list (line 108) | The 7 biological stages: name, length, colour, description |
| `Scene` class | line 169 | **Biology:** where everything is at time `t` |
| `App` class | line 480 | **Display:** window, buttons, mouse, 3D drawing, animation loop |

**Design decision worth mentioning:** the biology (`Scene`) does not know how anything is drawn, and the drawing code (`App`) does not know any biology. This is called *separation of concerns*. It means you could change the biology without touching the graphics, and the other way round.

---

## 2. The learning path (how you get from nothing to the final program)

| Step | File | New idea | What you see |
|---|---|---|---|
| 1 | `step1_window.py` | Window, canvas, drawing a circle | A blue circle |
| 2 | `step2_animation.py` | Animation loop with `root.after` | Circle falls onto a membrane line |
| 3 | `step3_3d_projection.py` | 3D points, rotation, perspective, painter's algorithm | A rotating sphere of dots you can drag |
| 4 | `step4_build_objects.py` | Building biology from balls | Membrane grid + LNP made of 4 lipid types + mRNA |
| 5 | `step5_timeline_endocytosis.py` | Time-driven stages, `lerp`, `ease`, Gaussian dip | LNP lands, membrane wraps it, endosome pinches off |
| 6 | `step6_ph_and_charge.py` | Henderson–Hasselbalch, colour blending | Lipids turn blue → orange as pH drops |
| 7 | `scripts/lnp_endosomal_escape_3d.py` | Escape pore, mRNA release, ribosomes, UI panel | The full simulation |

Run them in order. Before you move on from each one, change a number and predict what will happen. For example, change the speed in step 2 or `pitch` in step 3. Being able to predict the result is the best sign that you understand the code.

---

## 3. Deep dive: the programming

### 3.1 tkinter basics (step 1)

```python
root = tk.Tk()                       # the window
canvas = tk.Canvas(root, width=800, height=600, bg="#0a0e1a")
canvas.pack()                        # place it in the window
canvas.create_oval(x0, y0, x1, y1, fill="#6e8ce6")
root.mainloop()                      # hand control to tkinter
```

- **Screen coordinates:** (0, 0) is the **top-left** corner. *y increases downward*, the opposite of maths class. This is why the 3D code later uses `oy - y * s` (a minus sign).
- Colours are hex strings: `"#ff8c32"` = red 255, green 140, blue 50. The helper `hexc((255,140,50))` builds that string.
- `mainloop()` makes the program **event-driven**. It waits for things to happen (mouse, keys, timers) and calls your functions when they do.

### 3.2 The animation loop (step 2)

```python
def tick():
    update_positions()
    canvas.delete("all")   # erase
    draw_everything()      # redraw
    root.after(16, tick)   # run me again in 16 ms
```

- 16 ms is about 60 frames per second. The final program aims for that and actually gets about 30 fps, because it draws around 1,500 shapes per frame.
- **Why not `while True:`?** A `while` loop would never give control back to `mainloop()`, so the window would freeze and ignore the mouse. `after()` schedules the next frame and returns straight away.
- In the final script this is `App.tick` (line 662). It also uses **real elapsed time** (`time.perf_counter()`), so the animation runs at the same speed on fast and slow computers:

  ```python
  dt = now - self.last_time
  self.t += dt * self.speed.get()
  ```

### 3.3 Fake 3D (step 3), the core trick

tkinter can only draw flat shapes, so we do the 3D maths ourselves. Every object is a list of points `(x, y, z)`. Here y is up, and the membrane is the plane y = 0.

**Step A: rotate (camera angles).** Turning the camera is the same as turning the world the opposite way. We use the standard 2D rotation formula twice:

```
yaw (turn left/right, around the vertical y axis):
    x1 = x·cos(yaw) − z·sin(yaw)
    z1 = x·sin(yaw) + z·cos(yaw)

pitch (tilt up/down, around the horizontal x axis):
    y2 =  y·cos(pitch) + z1·sin(pitch)
    z2 = −y·sin(pitch) + z1·cos(pitch)
```

**Step B: perspective projection.** The camera sits a distance `D` in front of the world. A point's depth is `depth = z2 + D`. Then:

```
scale    = f / depth          (f = "focal length", basically zoom)
screen_x = centre_x + x1 · scale
screen_y = centre_y − y2 · scale
radius on screen = real radius · scale
```

Dividing by depth is what makes distant things smaller and closer to the centre, the way your eye sees.

*Worked example.* Take f = 600 and D = 17. A lipid with radius 0.2 at depth 17 is drawn with radius 0.2 × 600/17 ≈ **7 px**. The same lipid at depth 25 is 0.2 × 600/25 = **4.8 px**.

**Step C: painter's algorithm.** Circles drawn later cover earlier ones. So we sort by depth, **farthest first**, and draw in that order:

```python
drawn.sort(key=lambda a: -a[0])     # a[0] is depth
```

**Extras in the final script** (`App.render`, line 683):
- **Fog:** far balls are blended toward the background colour, which adds depth cues. `fog = clamp((depth − D + 4) / 22) · 0.7`
- **Highlight:** big balls get a small lighter circle near their top-left, so they look like shiny spheres.
- **Tiny balls (< 0.5 px) are skipped** to save time.
- **Smooth camera:** the camera does not jump to the LNP. It moves a fraction of the way each frame, which is exponential smoothing: `target = lerp(target, goal, dt·3)`.

### 3.4 Building objects out of balls (step 4)

**The Fibonacci sphere** (`fib_sphere`, line 70) spreads `n` points evenly over a sphere:
- Heights go evenly from +1 to −1: `y = 1 − 2(i + 0.5)/n`
- The ring radius at that height is `√(1 − y²)`, from Pythagoras, because `x² + y² + z² = 1`
- Each point is rotated by the **golden angle**, π(3 − √5) ≈ 137.5°. Because this angle is irrational, the points never line up in stripes, so the coverage is even.

The LNP, the endosome (170 points, radius 1.75), the ApoE positions and the proton pumps all use it.

**LNP composition.** Each of the 90 surface points is randomly given a lipid type in approximately the molar ratios of approved mRNA LNPs:

| Lipid | Approx. mol % | Role | Colour |
|---|---|---|---|
| Ionizable lipid (e.g. SM-102, ALC-0315) | ~50 % | Binds mRNA; becomes + charged in acid; drives escape | blue → orange |
| DSPC (phospholipid) | ~10 % | Helper / structure | white |
| Cholesterol | ~38 % (32 % here) | Stability, fills gaps | grey |
| PEG-lipid | ~1.5 % (8 % here so you can see it) | Stops clumping; sheds in the body | green |

`random.Random(7)` uses a fixed **seed**, so the "random" LNP is identical every run. That makes the results reproducible, which is a good habit in scientific code.

**Membrane:** a 20 × 20 grid of lipid heads spanning −7 to +7 in x and z.
**mRNA:** 48 beads on a 3D Lissajous curve, `(sin 2s, sin 3s, cos 2s · cos s)`, which looks like a tangled strand inside the LNP.
**Myofibrils:** 4 rows of balls along x, deep inside the cell. They are coloured in a repeating pattern of Z-line (pale), I-band (pink) and A-band (dark red), copying the striped sarcomeres that make skeletal muscle look striated.

### 3.5 Time drives everything (step 5)

The whole simulation is a **function of one number, `t`**. The `STAGES` list gives each stage a duration. `stage_at(t)` (line 157) returns:
- `s`: which stage (0–6)
- `u`: progress through that stage, from 0.0 to 1.0

Every position is then calculated with:

- **`lerp(a, b, u) = a + (b − a)·u`**, linear interpolation. At u = 0 you get a, at u = 1 you get b, and halfway you get the midpoint.
- **`ease(u) = u²(3 − 2u)`**, the "smoothstep" curve. It starts and ends with zero speed, so motion speeds up and slows down gently, like real movement.

*Example:* in stage 1 the LNP moves from (0, 2.6, 0) to (0, 1.25, 0): `vlerp(start, end, ease(u))`.

**Why compute from `t` instead of moving things a little each frame?** Because nothing depends on the previous frame, you can **jump to any moment** by clicking the timeline, and every run is exactly the same. Even the "random" proton ions get fixed start times when the program begins.

### 3.6 Endocytosis: the Gaussian dip (step 5)

The membrane height at each grid point is:

```
y = −depth · exp(−(x² + z²) / w²)        with w = 1.8
```

This is a **Gaussian (bell curve)** dent. It's deepest directly under the LNP (x = z = 0) and fades to flat at about 2w from the centre.
- While `depth` goes from 0 to 3.2, the LNP sinks with the membrane, so the membrane looks like it is wrapping around it.
- Then the **endosome sphere fades in** around the LNP and `depth` goes back to 0. The membrane is flat again, which shows the vesicle pinching off and the membrane resealing.

---

## 4. Deep dive: the biology, stage by stage

| # | Stage | Real biology | What the code does | Where |
|---|---|---|---|---|
| 1 | Approach & protein corona | After IM injection, the LNP is in interstitial fluid. PEG-lipids desorb, and proteins such as **ApoE** bind (the "protein corona"). | LNP glides down from y = 9. PEG balls drift outward and shrink to nothing. ApoE balls fly in and stick at radius 1.22. | `build`, PEG + ApoE sections |
| 2 | Receptor binding | ApoE is a ligand for the **LDL receptor** family. Receptors cluster at the binding site. | 12 purple receptors slide from random membrane positions to a ring under the LNP. | LDLR section |
| 3 | Endocytosis | The membrane invaginates (e.g. clathrin-mediated) and pinches off into an **early endosome**. | Gaussian dip deepens, endosome sphere fades in, membrane relaxes. | `depth()`, `lnp_center()` |
| 4 | Early endosome | The endosome moves inward. **V-ATPase** pumps H⁺ in using ATP. | Cyan pumps sit on the endosome. White H⁺ balls travel from outside to inside, each with a fixed start time. | protons section |
| 5 | Acidification | pH falls from about 6.5 (early) to about 5.0 (late endosome). Ionizable lipids get protonated (+). Receptors recycle. | pH follows a smooth curve. Lipid colour comes from the Henderson–Hasselbalch fraction. Endosome colour goes green → red. Receptors shrink away. | `ph()`, `charged` |
| 6 | Endosomal escape | Cationic ionizable lipids pair with **anionic endosomal lipids** (e.g. BMP/PS). They form non-bilayer **inverted hexagonal (H_II)** phases, which destabilise the membrane and let the mRNA out. | LNP lipids move outward into the endosome membrane (lipid mixing). A pore opens in one direction. The mRNA threads out bead by bead. | `pore()`, `fuse`, mRNA section |
| 7 | Translation | Ribosomes translate the mRNA into protein in the cytosol (for a vaccine, the antigen). | 4 ribosomes move along the strand one after another. Each grows a chain of protein beads. | ribosome section |

### 4.1 The key equation: why acid makes the lipid charged

Ionizable lipids have a tertiary amine. It is a weak base: `R₃N + H⁺ ⇌ R₃NH⁺`. From **Henderson–Hasselbalch**, the fraction that is protonated (charged) is:

```
fraction charged = 1 / (1 + 10^(pH − pKa))          pKa ≈ 6.4
```

| Location | pH | Charged |
|---|---|---|
| Blood / extracellular | 7.4 | **9 %**, mostly neutral (less toxic, longer circulation) |
| Early endosome | 6.5 | 44 % |
| At the pKa | 6.4 | 50 % (by definition) |
| Late endosome | 5.0 | **96 %**, strongly positive, which drives escape |

The pKa of about 6.4 is deliberately chosen by LNP designers, so the lipid is neutral in blood but charged in the endosome. That's the main design idea behind ionizable lipids, and the simulation colours each lipid with exactly this number (`charged`, around line 287 of the final script). Step 6 prints this table and lets you drag the pH slider.

### 4.2 How the escape pore is coded

- A fixed direction **P** is chosen as the rupture direction.
- For each point on the endosome, its angle to P is `acos(dot(direction, P))`. The **dot product** of two unit vectors equals the cosine of the angle between them.
- Points within the growing pore angle `theta` (up to 0.8 rad ≈ 46°) are pushed outward and shrunk. That opens a hole.
- **Lipid mixing:** LNP lipids move from radius 1.0 out to about 1.67, so they become part of the endosome membrane. This shows the LNP fusing with the endosomal membrane.
- **mRNA release:** each bead slides from its coiled position to a position on a wavy line leaving through the pore. The beads are **staggered** so the leading end moves first, which makes the strand look like it's threading out rather than teleporting. The two perpendicular axes Q and Q2 (built with a **cross product**) create the wave.

### 4.3 How translation is coded

Each ribosome has a progress value `g` from 0 to 1 along the 48 beads. Its position is found by interpolating between the two nearest beads. That's linear interpolation again, along the strand. The protein chain grows as `int(g · 16)` beads stacked away from the ribosome. Ribosomes start 0.17 of the stage apart, which gives a **polysome** (several ribosomes on one mRNA, as in real cells).

---

## 5. Simplifications (say these before your professor asks)

Knowing the limits of a model is part of doing science.

1. **Not to scale.** A real LNP is about 80–100 nm, a muscle fibre is about 50–100 µm wide, and mRNA is far longer than 48 beads.
2. **Not to time.** Real endosomal maturation takes minutes, and translation keeps going for hours or days.
3. **Escape is very inefficient in reality.** Only about 1–2 % of LNPs release their mRNA. Most end up in lysosomes and are degraded. The simulation shows the successful case.
4. **Uptake route.** LDL receptor/ApoE uptake is best known in **liver** cells. Muscle cells and the immune cells near the injection site also use other routes, such as macropinocytosis and other receptors. The model uses LDLR as a representative example.
5. **H_II phase.** This isn't modelled molecularly. It's shown as a pore opening.
6. **No physics engine.** Motion is scripted (keyframed). It isn't calculated from forces, diffusion or molecular dynamics.

---

## 6. Questions your professor might ask, with answers

**Q: Why tkinter and not a 3D library?**
It's built into Python, so it needs no installation and every computer can run it. It also meant implementing the 3D projection by hand, which shows I understand how 3D graphics works.

**Q: How do you get 3D on a 2D canvas?**
Each frame, every 3D point is rotated by the camera angles with sine/cosine rotation formulas, then projected by dividing by its depth (perspective). The points are sorted far-to-near and drawn as circles (painter's algorithm).

**Q: What decides when the lipids become charged?**
The Henderson–Hasselbalch equation with pKa 6.4. At pH 7.4 about 9 % are charged, and at pH 5.0 about 96 % are.

**Q: Why do the charged lipids cause escape?**
The positively charged ionizable lipids pair with negatively charged lipids in the endosomal membrane. The lipid pairs prefer a cone-shaped, non-bilayer (inverted hexagonal) arrangement, which breaks up the bilayer and opens a path for the mRNA into the cytosol.

**Q: How is the animation timed?**
Everything is calculated from one time variable `t`, divided into 7 stages. `lerp` and an easing curve interpolate positions inside each stage. Because nothing depends on the previous frame, you can jump anywhere on the timeline.

**Q: What would you improve?**
See section 7.

---

## 7. Ideas to extend it (shows you own the project)

- Add a **pKa slider** and watch how a different lipid would behave. For example, with pKa 5.5 escape happens later and less.
- Count escape efficiency: run 100 LNPs where only 1–2 escape and the rest go to a lysosome.
- Add a **nucleus** and **mitochondria** to the muscle cell.
- Use real numbers: plot fraction charged against pH with matplotlib, next to the animation.
- Link it to the MD work in this repo. For example, load protonation states from the `lnp` notebook and colour lipids from them.

---

## 8. Suggested 3-minute demo

1. **(20 s)** "This simulates how an mRNA lipid nanoparticle gets into a muscle cell and escapes the endosome. It's built in Python using only tkinter."
2. **(60 s)** Run it and talk through stages 1–4. Drag to rotate and show it's 3D.
3. **(45 s)** Pause in stage 5. Point at the pH bar: "pH dropped below the pKa of 6.4. Henderson–Hasselbalch says 96 % of the ionizable lipids are now positive. That's the colour change."
4. **(30 s)** Play stage 6–7: the pore opens, mRNA leaves, and ribosomes make protein.
5. **(25 s)** "How it works: 3D points, rotation, perspective division, painter's algorithm. Everything is computed from a single time variable. Limitations: not to scale, and real escape is only 1–2 %. I used an AI assistant to help write the code, and I built it up in these six steps to understand it."
