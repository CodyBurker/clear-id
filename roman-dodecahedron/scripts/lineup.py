"""Render the report's Fig. 3 lineup (top/left/front/right/back/bottom) of an STL.

usage: python3 lineup.py model.stl centre_z outdir [elev_deg] [top_roll bottom_roll tilt]
Faces follow the report's key (Hitchens 2023, Fig. 2): A base, B front.
Side views look at the vertices B/I/H (front), C/J/I (left), F/H/L (right),
D/E/K (back), raised elev_deg above horizontal (Fig. 3: about 10).
Top and bottom views look along the A axis; their in-plane rotation and the
slight camera lean are fitted to the Fig. 3 photos: top_roll 0, bottom_roll
288 (both measured from "front edge at the bottom of the image"), tilt 8
(top leans towards the bottom of the frame, bottom towards the upper right).
"""
import sys, subprocess, numpy as np
import faces_letters as FL

stl, cz, out = sys.argv[1], sys.argv[2], sys.argv[3]
elev = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
top_roll = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
bottom_roll = float(sys.argv[6]) if len(sys.argv) > 6 else 288.0
tilt = float(sys.argv[7]) if len(sys.argv) > 7 else 8.0
A_IDX, B_IDX = 1, 9                       # as in roman_dodecahedron_v5.scad
m = FL.letters(A_IDX, B_IDX); N = FL.N
up = -N[m["A"]]
def horiz(*L):
    v = sum(N[m[l]] for l in L); h = v - (v @ up) * up; return h / np.linalg.norm(h)
def tilt_cam(h, e):                         # raise the camera by e degrees
    e = np.radians(e); return np.cos(e) * h + np.sin(e) * up
hf = horiz("B", "I", "H")
def tilted(d, vu, tilt_deg, dir_deg):
    """tilt the camera direction d by tilt_deg towards screen angle dir_deg."""
    r = np.cross(vu, d); r /= np.linalg.norm(r)          # screen right
    t = np.radians(dir_deg); towards = np.cos(t) * r + np.sin(t) * vu
    e = np.radians(tilt_deg); dn = np.cos(e) * d + np.sin(e) * towards
    return dn / np.linalg.norm(dn), vu - (vu @ dn) * dn
def rolled(vu, d, roll_deg):
    t = np.radians(roll_deg); r = np.cross(vu, d)
    return np.cos(t) * vu + np.sin(t) * r
views = {
    "front": (tilt_cam(hf, elev), up),
    "left":  (tilt_cam(horiz("C", "J", "I"), elev), up),
    "right": (tilt_cam(horiz("F", "H", "L"), elev), up),
    "back":  (tilt_cam(horiz("D", "E", "K"), elev), up),
    "top":    tilted(up, rolled(-hf, up, top_roll), tilt, 270),
    "bottom": tilted(-up, rolled(-hf, -up, bottom_roll), tilt, 49),
}
for name, (d, vu) in views.items():
    subprocess.run([sys.executable, "-I", "render_stl.py", stl, f"{out}/lineup_{name}.png",
                    "--centre-z", cz, "--print-face", str(A_IDX), "--view", "dir",
                    "--dir=" + ",".join(map(str, d)), "--vup=" + ",".join(map(str, vu)),
                    "--size", "800", "--fov", "17.5", "--bg", "white"],
                   check=True, capture_output=True)
    print("rendered", name)
