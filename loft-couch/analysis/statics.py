"""
Statics / strength-of-materials check for a two-level "loft couch".

Edit the INPUTS block with your measured values and re-run:
    python statics.py
Figures are written to ../figures and a results table is printed.

Allowable stresses are approximate ASD reference values for SPF stud-grade
lumber (see NDS Supplement). Verify against the current NDS before relying on them.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

FIG = Path(__file__).resolve().parent.parent / "figures"
FIG.mkdir(exist_ok=True)

# ----------------------------- INPUTS (assumed - replace with measurements) -----------------------------
L       = 60.0        # in, deck length (along couch)             [ASSUMED]
D       = 34.0        # in, deck depth (front to back)            [ASSUMED]
H       = 52.0        # in, floor to top of deck                  [ASSUMED]
W_couch = 80.0        # lb, loveseat                              [ASSUMED]
W_deck  = 60.0        # lb, lumber + hardware                     [ASSUMED]
W_occ   = 2 * 200.0   # lb, two occupants @ 200 lb                [ASSUMED]
DLF     = 1.5         # dynamic load factor (sitting down)        [ASSUMED]
n_joist = 4           # joists spanning front-to-back             [from photos]
n_leg   = 4           # load-carrying legs                        [ASSUMED]
F_push  = 75.0        # lb, design shove / lean at seat height    [ASSUMED]

# 2x4 actual size and approximate SPF-stud reference design values (psi)
b, d = 1.5, 3.5
A = b * d
Fb, Fv, Fc, Fc_perp = 675.0, 135.0, 725.0, 425.0
E, Emin = 1.2e6, 0.51e6
screw_lat = 90.0      # lb allowable lateral per #9 structural screw in SPF [ASSUMED]
# --------------------------------------------------------------------------------------------------------

W_dead = W_couch + W_deck
P = W_dead + DLF * W_occ          # design vertical load, lb
print(f"Design vertical load P = {W_dead:.0f} dead + {DLF} x {W_occ:.0f} live = {P:.0f} lb\n")


def S_(o): return b * d**2 / 6 if o == "edge" else d * b**2 / 6
def I_(o): return b * d**3 / 12 if o == "edge" else d * b**3 / 12


res = {}  # name -> utilization (demand / allowable)

# 1) Long beams (front & back): simply supported between legs, UDL = half the load each
def beam(span, load, o):
    w = load / span
    M = w * span**2 / 8
    V = load / 2
    dfl = 5 * w * span**4 / (384 * E * I_(o))
    return dict(w=w, M=M, V=V, fb=M / S_(o), fv=1.5 * V / A, defl=dfl, limit=span / 360)

for o in ("edge", "flat"):
    r = beam(L, P / 2, o)
    print(f"Long beam 2x4 on {o:4s}: M={r['M']:.0f} in-lb  fb={r['fb']:.0f} psi (Fb={Fb:.0f})  "
          f"defl={r['defl']:.2f} in (L/360={r['limit']:.2f})")
rE = beam(L, P / 2, "edge")
res["Beam bending (2x4 on edge, full span)"] = rE["fb"] / Fb
res["Beam deflection (L/360)"] = rE["defl"] / rE["limit"]
res["Beam shear"] = rE["fv"] / Fv

# Same beam with a mid-span leg added (recommended retrofit)
rM = beam(L / 2, P / 4, "edge")
print(f"Long beam with mid-span leg (30 in): fb={rM['fb']:.0f} psi  util={rM['fb']/Fb:.2f}")

# 2) Joists (front-to-back), clear span ~ D - 3.5
Lj = D - 3.5
Pj = P / n_joist
Mj = Pj * Lj / 8
for o in ("edge", "flat"):
    print(f"Joist 2x4 on {o:4s}: fb={Mj/S_(o):.0f} psi  util={Mj/S_(o)/Fb:.2f}")
res["Joist bending (2x4 flat, worst case)"] = Mj / S_("flat") / Fb

# 3) Legs: axial compression with column stability factor Cp (NDS), weak-axis, K=1
Pleg = P / n_leg
slend = H / b
FcE = 0.822 * Emin / slend**2
c = 0.8
r_ = FcE / Fc
Cp = (1 + r_) / (2 * c) - np.sqrt(((1 + r_) / (2 * c))**2 - r_ / c)
Fc_allow = Fc * Cp
print(f"\nLeg: P={Pleg:.0f} lb  le/d={slend:.1f}  Cp={Cp:.2f}  Fc'={Fc_allow:.0f} psi  fc={Pleg/A:.0f} psi")
res["Leg compression + buckling (single 2x4)"] = (Pleg / A) / Fc_allow
res["Leg bearing on floor"] = (Pleg / A) / Fc_perp

# 4) Tipping about a long edge (free-standing, no wall tie)
W_tip = W_dead + W_occ
h_push = H + 10
F_tip = W_tip * (D / 2) / h_push
print(f"Tipping: overturning force = {F_tip:.0f} lb at {h_push:.0f} in height")
res[f"Tipping ({F_push:.0f} lb shove / overturn force)"] = F_push / F_tip

# 5) Racking: shove resisted by 4 leg-to-deck connections acting as cantilever legs (conservative)
Vleg = F_push / n_leg
Mjoint = Vleg * H
couple = Mjoint / d
cap = 4 * screw_lat
print(f"Racking: V/leg={Vleg:.1f} lb  M={Mjoint:.0f} in-lb  tie couple force={couple:.0f} lb vs {cap:.0f} lb capacity")
res[f"Corner-tie screws under {F_push:.0f} lb shove"] = couple / cap

print("\nUtilization summary (demand / allowable)")
for k, v in res.items():
    print(f"  {v:5.2f}  {k}")

# ------------------------------------------ Figures ------------------------------------------
# A) Beam loading + shear + moment
x = np.linspace(0, L, 200)
w = rE["w"]
R = P / 4
V = R - w * x
M = R * x - w * x**2 / 2
fig, ax = plt.subplots(3, 1, figsize=(7, 6.5), sharex=True)
ax[0].fill_between([0, L], [0, 0], [0.5, 0.5], color="#c8a165")
ax[0].set_ylim(-1.5, 2.8)
for xx in np.linspace(3, L - 3, 12):
    ax[0].annotate("", xy=(xx, 0.5), xytext=(xx, 2.0), arrowprops=dict(arrowstyle="->", color="tab:red"))
ax[0].plot([0], [-.35], "^k", ms=10)
ax[0].plot([L], [-.35], "^k", ms=10)
ax[0].text(L / 2, 2.3, f"w = {w:.1f} lb/in   (beam carries P/2 = {P/2:.0f} lb)", ha="center")
ax[0].axis("off")
ax[1].plot(x, V, color="tab:blue"); ax[1].fill_between(x, V, alpha=.2)
ax[1].set_ylabel("Shear V (lb)"); ax[1].axhline(0, color="k", lw=.6)
ax[2].plot(x, M, color="tab:green"); ax[2].fill_between(x, M, alpha=.2)
ax[2].set_ylabel("Moment M (in-lb)"); ax[2].set_xlabel("Position along beam (in)")
ax[2].annotate(f"Mmax = {M.max():.0f} in-lb", (L / 2, M.max()), xytext=(L * .55, M.max() * .55),
               arrowprops=dict(arrowstyle="->"))
fig.suptitle("Long deck beam: loading, shear and bending-moment diagrams")
fig.tight_layout(); fig.savefig(FIG / "beam_diagrams.png", dpi=160); plt.close(fig)

# B) Utilization chart
names = list(res.keys()); vals = [res[k] for k in names]
fig, ax = plt.subplots(figsize=(8.5, 4.2))
cols = ["#2e8b57" if v < 0.7 else "#e0a030" if v < 1.0 else "#c0392b" for v in vals]
ax.barh(names, vals, color=cols); ax.axvline(1, color="k", ls="--"); ax.invert_yaxis()
ax.set_xlabel("Utilization = demand / allowable   (1.0 = at limit)")
for i, v in enumerate(vals):
    ax.text(v + .02, i, f"{v:.2f}", va="center")
ax.set_xlim(0, max(1.5, max(vals) + .25))
ax.set_title("Member & connection utilization (design load, ASD)")
fig.tight_layout(); fig.savefig(FIG / "utilization.png", dpi=160); plt.close(fig)

# C) Beam stress vs span
spans = np.linspace(20, 72, 100)
def fb_edge(Ls, n=1): return (P / 2 * Ls / 8) / (n * S_("edge"))
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(spans, [fb_edge(s) for s in spans], label="single 2x4 on edge")
ax.plot(spans, [fb_edge(s, 2) for s in spans], label="doubled 2x4 (fastened together)")
ax.axhline(Fb, color="k", ls="--", label=f"Fb = {Fb:.0f} psi")
ax.axvline(L, color="gray", ls=":"); ax.axvline(L / 2, color="gray", ls=":")
top = ax.get_ylim()[1]
ax.text(L + .5, top * .9, "as built\n(60 in)", fontsize=8)
ax.text(L / 2 + .5, top * .9, "mid-span\nleg (30 in)", fontsize=8)
ax.set_xlabel("Unsupported beam span (in)"); ax.set_ylabel("Bending stress (psi)")
ax.legend(loc="upper left"); ax.set_title("Design sensitivity: beam bending stress vs. span")
fig.tight_layout(); fig.savefig(FIG / "span_sensitivity.png", dpi=160); plt.close(fig)

# D) Load-path schematic
fig, ax = plt.subplots(figsize=(7, 5)); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
ax.add_patch(plt.Rectangle((15, 78), 70, 10, fc="#e8dccb", ec="k"))
ax.text(50, 83, f"Couch {W_couch:.0f} lb + occupants {W_occ:.0f} lb x {DLF}", ha="center", fontsize=9)
ax.add_patch(plt.Rectangle((10, 64), 80, 6, fc="#c8a165", ec="k"))
ax.text(50, 66.5, "Deck: planks + 2x4 joists + beams", ha="center", fontsize=9)
for xx in (14, 86):
    ax.add_patch(plt.Rectangle((xx - 2, 10), 4, 54, fc="#d9b27c", ec="k"))
    ax.annotate("", xy=(xx, 10), xytext=(xx, 3), arrowprops=dict(arrowstyle="<-", color="tab:blue", lw=2))
    ax.text(xx, -3, f"R = {P/n_leg:.0f} lb", ha="center", color="tab:blue", fontsize=9)
for xx in np.linspace(20, 80, 9):
    ax.annotate("", xy=(xx, 70), xytext=(xx, 78), arrowprops=dict(arrowstyle="->", color="tab:red"))
ax.annotate("", xy=(88, 82), xytext=(99, 82), arrowprops=dict(arrowstyle="->", color="tab:purple", lw=2))
ax.text(94, 90, f"lateral shove\n{F_push:.0f} lb", color="tab:purple", fontsize=9, ha="center")
ax.add_patch(plt.Rectangle((8, 58), 8, 6, fc="silver", ec="k")); ax.add_patch(plt.Rectangle((84, 58), 8, 6, fc="silver", ec="k"))
ax.text(30, 60, "Simpson tie ->", fontsize=8, ha="center"); ax.text(70, 60, "<- Simpson tie", fontsize=8, ha="center")
ax.set_title("Load path and free-body schematic (front elevation)")
fig.savefig(FIG / "load_path.png", dpi=160, bbox_inches="tight"); plt.close(fig)
