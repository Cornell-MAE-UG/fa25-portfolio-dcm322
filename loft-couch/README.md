# Loft Couch: a Two-Level Dorm Seating and Lounge Structure

A self-designed, self-built elevated couch platform with a lounge area underneath. I designed the frame in dimensional lumber, tied it together with structural connectors, and then checked it with a statics and strength-of-materials analysis in Python.

![Front view](images/front-view.jpg)

## Design goals

- Put a full loveseat at the upper level and a bean-bag lounge space underneath.
- Use only dimensional lumber and off-the-shelf connectors (no welding, no custom fabrication).
- Be a dorm-friendly build that can be bolted and screwed together without damaging the room.
- Carry two adults plus the couch, and resist being pushed or bumped.

## Structure overview

| Subsystem | What it is | Photo |
|---|---|---|
| Legs | 2x4 uprights, with 2x4 rungs between them that double as a ladder and as cross-bracing | ![](images/side-ladder.jpg) |
| Deck frame | 2x4 beams along the length, 2x4 joists front to back, 2x decking on top | ![](images/underside-joists.jpg) |
| Corner joints | Simpson Strong-Tie tension ties (looks like the DTT-series, ESR-2523) fastened with structural screws | ![](images/simpson-tie-detail.jpg) |
| Couch attachment | Steel L-brackets screwed to the couch frame and to a 2x4 rail on the deck | ![](images/couch-mounting-brackets.jpg) |

More detail shots:

![Corner connectors](images/corner-connectors.jpg)
![Beam to couch bracket](images/beam-couch-bracket.jpg)
![Ladder rung](images/ladder-rung.jpg)

## Load path

Vertical load travels from the couch and occupants into the deck planks, through the joists into the long beams, across the corner ties into the legs, and into the floor. The ties are the only moment-resisting links between the deck and the legs, so they govern sideways stiffness.

![Load path](figures/load_path.png)

## Analysis

All numbers come from [`analysis/statics.py`](analysis/statics.py). Every input is at the top of the file, so you can replace my assumptions with measured values and re-run it.

### Assumptions

These are **estimates from photos, not measurements**, and are the first thing to change.

| Input | Value |
|---|---|
| Deck size | 60 in x 34 in |
| Deck height | 52 in |
| Couch weight | 80 lb |
| Lumber and hardware | 60 lb |
| Occupants | 2 x 200 lb |
| Dynamic load factor (sitting down) | 1.5 |
| Lumber | SPF stud grade 2x4 (1.5 x 3.5 in): Fb = 675 psi, Fv = 135 psi, Fc = 725 psi, E = 1.2e6 psi |
| Lateral shove | 75 lb at seat height |
| Screw lateral capacity | 90 lb per structural screw |

Design vertical load: **P = 140 lb dead + 1.5 x 400 lb live = 740 lb**.

### Method

1. **Beams.** Each long beam is a simply supported 2x4 on edge between legs, carrying P/2 as a uniform load. Check bending, shear and deflection (limit L/360).

   M_max = wL²/8 and f_b = M/S, where S = bd²/6 = 3.06 in³ for a 2x4 on edge.

2. **Joists.** Front-to-back 2x4s with a clear span of about 30 in, carrying P/4 each. Checked in the worst-case flat orientation.
3. **Legs.** Axial compression with the NDS column stability factor C_p, buckling about the weak axis with an unbraced length equal to the deck height.
4. **Tipping.** Overturning force about a long edge, F = W(D/2)/h, compared against a 75 lb shove.
5. **Racking.** The shove is split across four legs, the resulting moment at each leg top is converted to a couple across the tie plate, and that is compared against screw capacity.

![Beam diagrams](figures/beam_diagrams.png)

### Results

![Utilization](figures/utilization.png)

| Check | Demand / allowable | Verdict |
|---|---|---|
| Beam bending (2x4 on edge, 60 in span) | **1.34** | Exceeds limit (conservative model, see below) |
| Beam deflection | 0.97 | Marginal (0.16 in vs 0.17 in limit) |
| Beam shear | 0.39 | OK |
| Joist bending (flat, worst case) | 0.80 | OK |
| Leg compression and buckling | 0.12 | OK, large margin |
| Leg bearing on floor | 0.08 | OK |
| Tipping (75 lb shove) | 0.51 | OK, but only about 148 lb is needed to tip it |
| Corner-tie screws under shove | 0.77 | OK, limited margin |

### What the analysis says

- **The legs are not the problem.** Each leg carries about 185 lb against a buckling-reduced capacity of roughly 1,600 lb.
- **The long beam span is the weak link.** A single 2x4 spanning 60 in with no intermediate support is at 134% of allowable bending stress under the full dynamic design load. The model is deliberately conservative: it ignores the couch's own 2x4 rails and the decking planks, which stiffen the beam in reality (composite action), and it assumes the worst-case simultaneous load. It is still the right place to add margin.
- **Adding a mid-span leg cuts beam bending stress by about 75%.** Halving the span cuts the moment by 4x, so utilization drops from 1.34 to **0.34**. Doubling the beam (two 2x4s fastened face to face) gets a similar benefit without changing the layout.

![Span sensitivity](figures/span_sensitivity.png)

- **Stiffness in the racking direction depends on the corner ties.** At 75 lb of shove the ties are at 77% of screw capacity. A diagonal knee brace in each frame plane, or tying the back legs to a wall stud where the room allows it, would raise this margin substantially.
- **It can tip.** A free-standing structure like this overturns at about 150 lb of lateral force at seat height. Anchoring the top rail to the wall (with permission in a dorm) removes the tipping mode.

## What I would change in v2

1. Add a center leg, or double the long beams, to bring beam bending well under the allowable stress.
2. Add diagonal bracing in both directions to stiffen against racking.
3. Anchor the back of the deck to the wall.
4. Replace assumed values with measured dimensions and a scale-weighed couch, and load-test the structure with sandbags in steps while measuring deflection against the model.

## Limitations

- Dimensions, weights and the screw capacity are estimates, and lumber properties are approximate stud-grade values. The legs also look like they may be a denser species than SPF, which would help.
- Joints are treated as pinned for gravity load and as simple couples for racking. A frame analysis (FEA) would capture the real joint stiffness.
- This is a hobby and educational analysis, not a stamped engineering design. Do not rely on it as proof of safety, and check the connector manufacturer's published allowable loads before depending on any joint.

## Repo layout

```
loft-couch/
├── README.md
├── images/          # project photos (backgrounds blurred)
├── figures/         # generated diagrams and charts
└── analysis/
    └── statics.py   # parametric statics calculation (numpy, matplotlib)
```

## Run the analysis

```bash
pip install numpy matplotlib
cd analysis
python statics.py
```
