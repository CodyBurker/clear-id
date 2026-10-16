"""Printability checks on the print-oriented STL.

usage: python3 -I printcheck.py model.stl centre_z print_face hole_d_json out_section.png
"""
import sys, json, numpy as np, trimesh
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import validate as V

path, cz, pf, hd, sec_png = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), json.loads(sys.argv[4]), sys.argv[5]
m = trimesh.load_mesh(path, process=False); m.merge_vertices(digits_vertex=9)
N = V.print_frame_normals(pf); C = np.array([0, 0, cz])
out = {}

# 1. Face-wall thickness through the relief zone: for each face shoot rays
#    inward along -n at radii from the hole lip to the edge of the ring field,
#    and measure the distance from the outer surface hit to the cavity hit.
inr = float(sys.argv[6]) if len(sys.argv) > 6 else 27.2
per_face = []
for i, n in enumerate(N):
    u = np.cross(n, [0, 0, 1] if abs(n[2]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u); w = np.cross(n, u)
    rh = hd[i] / 2
    origins = []
    for r in np.linspace(rh + 1.3, 14.5, 40):          # beyond the rounded lip
        for t in np.linspace(0, 2 * np.pi, 48, endpoint=False):
            origins.append(C + n * (inr + 5) + u * r * np.cos(t) + w * r * np.sin(t))
    origins = np.array(origins); dirs = np.tile(-n, (len(origins), 1))
    locs, ri, _ = m.ray.intersects_location(origins, dirs, multiple_hits=True)
    d = np.einsum("ij,ij->i", locs - origins[ri], dirs[ri])
    th = []
    for k in range(len(origins)):
        dk = np.sort(d[ri == k])
        if len(dk) >= 2:
            th.append(dk[1] - dk[0])
    per_face.append(float(np.min(th)))
out["face_wall_min_mm_per_face(grooved zone)"] = [round(x, 2) for x in per_face]
out["face_wall_min_mm"] = round(min(per_face), 2)

# 2. General local thickness: inward ray from sampled surface points.
pts, fid = trimesh.sample.sample_surface_even(m, 40000, seed=1)
nrm = m.face_normals[fid]
locs, ri, _ = m.ray.intersects_location(pts - nrm * 1e-3, -nrm, multiple_hits=False)
th = np.full(len(pts), np.inf); th[ri] = np.linalg.norm(locs - pts[ri], axis=1)
fin = th[np.isfinite(th)]
out["local_thickness_percentiles_mm(p1,p5,p50)"] = [round(float(np.percentile(fin, q)), 2) for q in (1, 5, 50)]
thin = np.isfinite(th) & (th < 1.2)
# classify thin samples: on a hole lip (close to a face axis) vs elsewhere
def near_lip(p):
    for i, n in enumerate(N):
        v = p - C; a = np.dot(v, n); rr = np.linalg.norm(v - a * n)
        if a > inr - 4.5 and rr < hd[i] / 2 + 1.6:
            return True
    return False
def on_border_bead(p):
    # low ridge where the ring border dip meets the edge rounding: the ray
    # crosses the ~1 mm wide bead sideways and exits into the dip
    v = p - C; i = int(np.argmax(N @ v)); a = v @ N[i]; rr = np.linalg.norm(v - a * N[i])
    return abs(a - inr) < 0.5 and rr > 0.58 * inr
lip = sum(near_lip(p) for p in pts[thin])
bead = sum((not near_lip(p)) and on_border_bead(p) for p in pts[thin])
out["samples_thinner_than_1.2mm"] = int(thin.sum())
out["  ...of which on rounded hole lips/chamfers (expected edge artefact)"] = int(lip)
out["  ...of which on the face-border bead (surface ridge on full wall)"] = int(bead)
out["  ...unexplained"] = int(thin.sum() - lip - bead)

# 3. Bed contact and overhangs (Z up, bed at z=0).
zmin = float(m.bounds[0][2])
tri_z = m.triangles_center[:, 2]; nz = m.face_normals[:, 2]
bed = (tri_z < zmin + 0.01) & (nz < -0.99)
bed_mesh = m.submesh([np.where(bed)[0]], append=True)
out["bed_z_mm"] = round(zmin, 3)
out["bed_contact_area_mm2"] = round(float(m.area_faces[bed].sum()), 1)
out["bed_contact_islands"] = len(bed_mesh.split(only_watertight=False)) if bed.any() else 0
over = (nz < -np.cos(np.radians(45))) & ~bed
out["overhang_area_mm2(>45deg from vertical, needs support)"] = round(float(m.area_faces[over].sum()), 1)
out["total_area_mm2"] = round(float(m.area), 1)
out["height_mm"] = round(float(m.bounds[1][2] - zmin), 2)
print(json.dumps(out, indent=1))

# 4. Cross-section through the centre, plane containing the print axis and the
#    axis of face 4 (the "front" face of the photo view).
n4 = N[4]; pn = np.cross(n4, [0, 0, 1]); pn /= np.linalg.norm(pn)
sec = m.section(plane_origin=C, plane_normal=pn)
p2, T = sec.to_2D()
fig, ax = plt.subplots(figsize=(7, 7), dpi=140)
for poly in p2.polygons_full:
    xs, ys = poly.exterior.xy; ax.fill(xs, ys, color="#8a7a55", ec="#3a3020", lw=0.6)
    for hole in poly.interiors:
        xs, ys = hole.xy; ax.fill(xs, ys, color="white", ec="#3a3020", lw=0.6)
ax.set_aspect("equal"); ax.grid(alpha=0.25)
ax.set_title("Cross-section through centre (final STL)\nwall cut, open holes and knob roots", fontsize=10)
ax.set_xlabel("mm"); ax.set_ylabel("mm")
fig.tight_layout(); fig.savefig(sec_png)
