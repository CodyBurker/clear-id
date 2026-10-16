"""Render the report's Fig. 3 lineup (top/left/front/right/back/bottom) of an STL.

usage: python3 lineup.py model.stl centre_z outdir [elev_deg]
Faces follow the report's key (Hitchens 2023, Fig. 2): A base, B front,
side views look at the vertices B/I/H (front), C/J/I (left), F/H/L (right),
D/E/K (back); top looks down on G, bottom looks up at A.
"""
import sys, subprocess, numpy as np
import faces_letters as FL

stl, cz, out = sys.argv[1], sys.argv[2], sys.argv[3]
elev = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
A_IDX, B_IDX = 1, 9                       # as in roman_dodecahedron_v5.scad
m = FL.letters(A_IDX, B_IDX); N = FL.N
up = -N[m["A"]]
def horiz(*L):
    v = sum(N[m[l]] for l in L); h = v - (v @ up) * up; return h / np.linalg.norm(h)
def tilt(h, e):                             # raise the camera by e degrees
    e = np.radians(e); return np.cos(e) * h + np.sin(e) * up
hf = horiz("B", "I", "H")
views = {
    "front": (tilt(hf, elev), up),
    "left":  (tilt(horiz("C", "J", "I"), elev), up),
    "right": (tilt(horiz("F", "H", "L"), elev), up),
    "back":  (tilt(horiz("D", "E", "K"), elev), up),
    "top":   (up, -hf),                     # front edge at the bottom of the image
    "bottom": (-up, -hf),                   # front edge at the bottom of the image (as in Fig. 3)
}
for name, (d, vu) in views.items():
    subprocess.run([sys.executable, "-I", "render_stl.py", stl, f"{out}/lineup_{name}.png",
                    "--centre-z", cz, "--print-face", str(A_IDX), "--view", "dir",
                    "--dir=" + ",".join(map(str, d)), "--vup=" + ",".join(map(str, vu)),
                    "--size", "800", "--fov", "17.5", "--bg", "white"],
                   check=True, capture_output=True)
    print("rendered", name)
