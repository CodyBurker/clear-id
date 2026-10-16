"""Render an exported dodecahedron STL with VTK (offscreen), photo-like view.

usage: python3 -I render_stl.py model.stl out.png [--centre-z Z --print-face K]
       [--view photo|print|inside] [--size 1000]
The STL is drawn exactly as exported; only a rigid camera/model transform is applied.
"""
import argparse, numpy as np, vtk
from vtk.util.numpy_support import numpy_to_vtk

PHI = (1 + 5 ** 0.5) / 2
FACE_N = np.array([(1,0,-PHI),(-1,0,-PHI),(-PHI,-1,0),(-PHI,1,0),(0,-PHI,1),(0,-PHI,-1),
                   (PHI,-1,0),(-1,0,PHI),(1,0,PHI),(0,PHI,-1),(PHI,1,0),(0,PHI,1)], float)
FACE_N /= np.linalg.norm(FACE_N, axis=1)[:, None]

def rot(axis, ang):
    axis = np.asarray(axis, float); axis /= np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K

ap = argparse.ArgumentParser()
ap.add_argument("stl"); ap.add_argument("out")
ap.add_argument("--centre-z", type=float, default=None)
ap.add_argument("--print-face", type=int, default=3)
ap.add_argument("--view", default="photo")
ap.add_argument("--size", type=int, default=1000)
ap.add_argument("--elev", type=float, default=12.0)
ap.add_argument("--azim", type=float, default=0.0)
ap.add_argument("--fov", type=float, default=17.5)
ap.add_argument("--front-face", type=int, default=4)
ap.add_argument("--roll", type=float, default=0.0)
ap.add_argument("--ortho", type=float, default=0.0, help="parallel projection, half-height in mm")
ap.add_argument("--dir", default=None, help="view: camera direction x,y,z (native .scad frame)")
ap.add_argument("--vup", default=None, help="view: screen-up vector x,y,z (native .scad frame)")
ap.add_argument("--bg", default="grad", help="grad or white")
a = ap.parse_args()

reader = vtk.vtkSTLReader(); reader.SetFileName(a.stl); reader.Update()
poly = reader.GetOutput()

# Rigid transform: undo the print orientation (if any) so the model is in the
# .scad's native frame, centred on the dodecahedron centre.
M = np.eye(4)
if a.centre_z is not None:
    pn = FACE_N[a.print_face]; m = -pn
    Rp = rot([-m[1], m[0], 0], -np.arccos(m[2]))          # native -> print
    T = np.eye(4); T[:3, 3] = [0, 0, -a.centre_z]
    Rinv = np.eye(4); Rinv[:3, :3] = Rp.T
    M = Rinv @ T

# Photo view: face 4 towards the camera, its vertex 9 pointing down.
VERTS = np.array([(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)] +
                 [(0, s1 / PHI, s2 * PHI) for s1 in (-1, 1) for s2 in (-1, 1)] +
                 [(s1 / PHI, s2 * PHI, 0) for s1 in (-1, 1) for s2 in (-1, 1)] +
                 [(s1 * PHI, 0, s2 / PHI) for s1 in (-1, 1) for s2 in (-1, 1)], float)
front = FACE_N[a.front_face]
fv = [v for v in VERTS if np.dot(v / np.linalg.norm(v), front) > 0.75]
vb = min(fv, key=lambda v: v[2])          # face vertex lowest in z points down
fc = front * np.dot(vb, front)
up = fc - vb; up -= np.dot(up, front) * front; up /= np.linalg.norm(up)
up = rot(front, np.radians(a.roll)) @ up

tf = vtk.vtkTransform(); tf.SetMatrix(M.flatten().tolist())
tpf = vtk.vtkTransformPolyDataFilter(); tpf.SetInputData(poly); tpf.SetTransform(tf); tpf.Update()

normals = vtk.vtkPolyDataNormals(); normals.SetInputConnection(tpf.GetOutputPort())
normals.SetFeatureAngle(35); normals.SplittingOn(); normals.ConsistencyOn(); normals.Update()

mapper = vtk.vtkPolyDataMapper(); mapper.SetInputConnection(normals.GetOutputPort())
actor = vtk.vtkActor(); actor.SetMapper(mapper)
p = actor.GetProperty()
p.SetColor(0.42, 0.40, 0.30)          # dark weathered bronze
p.SetAmbient(0.12); p.SetDiffuse(0.85); p.SetSpecular(0.35); p.SetSpecularPower(18)
p.SetSpecularColor(1.0, 0.85, 0.55)
p.SetInterpolationToPhong()

ren = vtk.vtkRenderer(); ren.AddActor(actor)
if a.bg == "white":
    ren.SetBackground(1, 1, 1)
else:
    ren.SetBackground(0.86, 0.85, 0.83); ren.SetBackground2(0.97, 0.96, 0.94); ren.GradientBackgroundOn()
ren.SetUseFXAA(True)
win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetSize(a.size, a.size); win.AddRenderer(ren)
win.SetMultiSamples(0)

cam = ren.GetActiveCamera()
right = np.cross(up, front)            # screen-right when looking along -front
if a.view == "photo":
    d = rot(right, np.radians(a.elev)) @ front
    d = rot(up, np.radians(a.azim)) @ d
    vu = up
elif a.view == "print":                # as it sits on the bed, from the side
    d = np.array([0.0, -1.0, 0.35]); vu = np.array([0, 0, 1.0])
    pn = FACE_N[a.print_face]; m = -pn
    Rp = rot([-m[1], m[0], 0], -np.arccos(m[2]))
    d = Rp.T @ (d / np.linalg.norm(d)); vu = Rp.T @ vu
elif a.view == "dir":                  # explicit camera direction / up vector
    d = np.array([float(t) for t in a.dir.split(",")]); d /= np.linalg.norm(d)
    vu = np.array([float(t) for t in a.vup.split(",")])
    vu = vu - (vu @ d) * d; vu /= np.linalg.norm(vu)
elif a.view == "side":                 # resting on --print-face, looking at --front-face
    vu = -FACE_N[a.print_face]
    h = front - (front @ vu) * vu; h /= np.linalg.norm(h)
    d = rot(np.cross(vu, h), -np.radians(a.elev)) @ h
    d = rot(vu, np.radians(a.azim)) @ d
else:
    d = front; vu = up
cam.SetFocalPoint(0, 0, 0); cam.SetPosition(*(d * 300)); cam.SetViewUp(*vu)
if a.ortho > 0:
    cam.SetParallelProjection(True); cam.SetParallelScale(a.ortho)
else:
    cam.SetParallelProjection(False); cam.SetViewAngle(a.fov)
ren.ResetCameraClippingRange()

def light(pos, inten, col):
    L = vtk.vtkLight(); L.SetLightTypeToSceneLight(); L.SetPosition(*pos); L.SetFocalPoint(0, 0, 0)
    L.SetIntensity(inten); L.SetColor(*col); L.SetPositional(False); ren.AddLight(L)
if a.view in ("dir", "side"):            # light relative to this camera, not the photo view
    up = vu; right = np.cross(vu, d)
key_dir = d * 0.5 + right * 1.0 + up * 0.6     # warm key from the right, like the photo
light(key_dir * 200, 0.95, (1.0, 0.86, 0.6))
light((d * 0.8 - right * 0.9 + up * 0.3) * 200, 0.35, (0.75, 0.82, 0.9))
light((d + up * 1.5) * 200, 0.25, (1, 1, 1))
ren.LightFollowCameraOff(); ren.AutomaticLightCreationOff()

win.Render()
w2i = vtk.vtkWindowToImageFilter(); w2i.SetInput(win); w2i.ReadFrontBufferOff(); w2i.Update()
wr = vtk.vtkPNGWriter(); wr.SetFileName(a.out); wr.SetInputConnection(w2i.GetOutputPort()); wr.Write()
print("rendered", a.stl, poly.GetNumberOfPoints(), "points", poly.GetNumberOfCells(), "triangles ->", a.out)
