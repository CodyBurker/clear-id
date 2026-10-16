"""Validate a Roman-dodecahedron STL: integrity, connectivity, openings, size, wall."""
import sys, json, numpy as np, trimesh

PHI = (1 + 5 ** 0.5) / 2
# Dodecahedron face normals (same orientation as the .scad source)
_n = []
for a, b in [(0, 1), (1, 2), (2, 0)]:
    for s1 in (1, -1):
        for s2 in (1, -1):
            v = [0, 0, 0]; v[a] = s1 * 1.0; v[b] = s2 * PHI
            _n.append(v)
# The scad uses normals like (0.5257,0,-0.8507) = (1, 0, -phi)/|.|: axes (x,z),(y,x),(z,y)
NORMALS = []
for v in [(1,0,-PHI),(-1,0,-PHI),(-PHI,-1,0),(-PHI,1,0),(0,-PHI,1),(0,-PHI,-1),(PHI,-1,0),(-1,0,PHI),(1,0,PHI),(0,PHI,-1),(PHI,1,0),(0,PHI,1)]:  # same order as face_n in the .scad
    v = np.array(v, float); NORMALS.append(v / np.linalg.norm(v))
NORMALS = np.array(NORMALS)

def print_frame_normals(print_face):
    """Rotate NORMALS the same way the .scad does: face `print_face` -> -Z."""
    pn = NORMALS[print_face]; m = -pn
    axis = np.array([-m[1], m[0], 0.0]); axis /= np.linalg.norm(axis)
    ang = -np.arccos(m[2])
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    R = np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K
    return (R @ NORMALS.T).T

def report(path, hole_d=None, centre=None, normals=None):
    m = trimesh.load_mesh(path, process=False)
    m.merge_vertices(digits_vertex=9)  # merge only exact duplicates (STL stores per-facet vertices)
    r = {}
    r["file"] = path
    r["triangles"] = int(len(m.faces)); r["vertices"] = int(len(m.vertices))
    ext = m.bounds[1] - m.bounds[0]
    r["bbox_mm"] = [round(float(e), 2) for e in ext]
    r["max_radius_mm"] = round(float(np.linalg.norm(m.vertices, axis=1).max()), 2)
    r["watertight"] = bool(m.is_watertight)
    r["winding_consistent"] = bool(m.is_winding_consistent)
    r["volume_cm3"] = round(float(m.volume) / 1000, 2)
    r["volume_positive"] = bool(m.volume > 0)
    edges = m.edges_sorted
    _, counts = np.unique(edges, axis=0, return_counts=True)
    r["nonmanifold_edges(not_2_faces)"] = int((counts != 2).sum())
    bodies = m.split(only_watertight=False)
    r["connected_bodies"] = len(bodies)
    r["euler_number"] = int(m.euler_number)
    r["genus(expected 11 for hollow shell with 12 through-holes)"] = int((2 - m.euler_number) // 2)
    r["degenerate_faces"] = int((m.area_faces < 1e-10).sum())
    r["duplicate_faces"] = int(len(m.faces) - len(np.unique(np.sort(m.faces, axis=1), axis=0)))
    # Through-opening ray test: from 60mm outside along each face axis to body centre.
    c = m.bounding_box.centroid if centre is None else np.asarray(centre, float)
    hit = []
    for i, n in enumerate(NORMALS if normals is None else normals):
        origins, dirs, tags = [], [], []
        # centre ray plus rays on circles at 25/50/70% of hole radius (if known)
        rad = (hole_d[i] / 2 if hole_d else 3.0)
        pts = [(0, 0)] + [(f * rad * np.cos(t), f * rad * np.sin(t)) for f in (0.25, 0.5, 0.7) for t in np.linspace(0, 2*np.pi, 12, endpoint=False)]
        u = np.cross(n, [0, 0, 1] if abs(n[2]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u); w = np.cross(n, u)
        for (a, b) in pts:
            origins.append(c + n * 60 + u * a + w * b); dirs.append(-n)
        locs, ray_idx, _ = m.ray.intersects_location(np.array(origins), np.array(dirs), multiple_hits=True)
        # count hits before reaching the centre plane (distance < 60 along ray)
        blocked = set()
        for L, ri in zip(locs, ray_idx):
            if np.dot(L - origins[ri], -n) < 60 - 1e-6:
                blocked.add(int(ri))
        hit.append(len(blocked))
    r["blocked_rays_per_face(of 37, centre+3 rings)"] = hit
    r["all_12_holes_open"] = all(h == 0 for h in hit)
    return m, r

if __name__ == "__main__":
    hd = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    if len(sys.argv) > 4:   # print-oriented file: centre z, print face index
        m, r = report(sys.argv[1], hd, [0, 0, float(sys.argv[3])], print_frame_normals(int(sys.argv[4])))
    else:
        m, r = report(sys.argv[1], hd)
    print(json.dumps(r, indent=1))
