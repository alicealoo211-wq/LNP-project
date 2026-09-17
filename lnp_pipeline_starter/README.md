# LNP Pipeline (Starter Code)

A beginner-friendly Python starter for the project *"Predicting Endosomal
Escape: A Python-Based Analysis of pH-Responsive Lipid Nanoparticle Behavior."*

You do **not** need to understand all of this yet. It's a working skeleton you
can run today and grow into. Everything is commented in plain English.

## What's here

```
lnp_pipeline_starter/
├── demo.py              <- RUN THIS FIRST. A full working example.
├── requirements.txt     <- the packages to install
├── README.md            <- this file
├── lnp_pipeline/        <- the toolkit, split into small labelled files
│   ├── composition.py   <- recipe numbers (N/P ratio). Start reading here.
│   ├── metrics.py       <- the measurements (curvature, tail angle, water)
│   ├── transition.py    <- finds WHEN the shape change happens
│   ├── io.py            <- opens real simulation files (needs MDAnalysis)
│   └── visualize.py     <- makes graphs
└── tests/
    └── test_pipeline.py <- checks that the functions give correct answers
```

## How to run it (three steps)

1. **Install Python 3** (if you haven't) from python.org.

2. **Install the packages.** Open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   ```
   (For just the demo, `pip install numpy matplotlib` is enough.)

3. **Run the demo:**
   ```
   python demo.py
   ```
   It prints results and saves a graph called `curvature_demo.png`.

## Run the tests

```
python tests/test_pipeline.py
```
You should see every check print `PASS`.

## A suggested first week

- Day 1: Run `demo.py`. Just watch it work.
- Day 2: Open `composition.py` and read it top to bottom. Change the recipe
  numbers in `demo.py` and re-run to see the N/P ratio change.
- Day 3: Read `metrics.py`. These three functions are the science.
- Day 4: Read `transition.py` and `visualize.py`.
- Later: install `MDAnalysis`, get one real trajectory, and use `io.py` to
  open it — then feed its real heights into `metrics.membrane_curvature()`.

The demo uses **pretend data** so it runs before you have any real files. The
measurement, detection, and plotting code is real and will work on real data
once you load it with `io.py`.
