// Roman dodecahedron replica, v3 (FDM-printable).
// Inspired by the Norton Disney dodecahedron photo; an interpretation, not a scan.
//
// Build:  openscad --backend=manifold -o roman_dodecahedron_v3.stl roman_dodecahedron_v3.scad
// (OpenSCAD 2024+ "Manifold" backend recommended; CGAL also works but is slow.)
//
// What changed from v2
//  * Each opening is cut by ONE revolved cutter that runs from 1.5 mm inside the
//    cavity to 2 mm outside the face, so it always pierces the full wall
//    (v2 left a ~0.5 mm membrane on every face).
//  * The same cutter carves the rounded hole lip and shallow concentric grooves
//    into the face (no raised tube rings).  Grooves never cut deeper than
//    groove_depth_max, so the wall stays >= wall - groove_depth_max.
//  * Outer body = hull of spheres -> softly rounded, cast-looking edges.
//  * Knobs are one revolved profile: oblate, worn-flat ball + thick neck that
//    flares into the corner, blended with a smooth-max fillet.
//  * Exported in print orientation, resting on five small flats ground onto the
//    knob tips around one face (print_pads).

/* [Size] */
body_inradius     = 27.2;  // centre -> outer face plane (mm). Sets overall size.
wall              = 3.2;   // face wall thickness (mm)
edge_round        = 2.8;   // outer edge/corner rounding radius (mm)
inner_round       = 0.8;   // cavity edge rounding radius (mm)

/* [Openings] (one per face, all different) */
hole_d = [13, 10, 15, 17, 18, 14, 9, 19, 16, 12, 11, 8];
hole_lip_r        = 1.0;   // rounding radius of the outer hole edge
hole_inner_chamfer= 0.5;   // chamfer on the cavity side of each hole
groove_depth_max  = 0.62;  // deepest groove below the face plane
ring_field_margin = 0.9;   // keep grooves this far inside the flat face area

/* [Knobs] */
knob_r            = 3.7;   // ball radius (lateral)
knob_squash       = 0.90;  // axial/lateral ratio of the ball (worn, oblate)
knob_flat         = 0.90;  // tip ground flat at this fraction of axial semi-axis
knob_ball_z       = 3.0;   // ball centre height above the corner surface
knob_neck_r       = 2.4;   // neck radius
knob_neck_z       = 0.8;   // where the root flare starts (above corner surface)
knob_root_r       = 3.2;   // radius the root flare tends to
knob_root_len     = 1.6;   // length of the flare transition
knob_root_slope   = 0.10;  // extra widening per mm further into the corner
knob_blend        = 0.9;   // fillet size between ball and neck

/* [Irregularity] (small, deterministic) */
seed              = 7;
jitter            = 1.0;   // 0 = perfectly regular, 1 = default

/* [Print] */
print_orientation = true;  // rest on the five knobs around print_face
print_face        = 3;     // index into face_n
pad_depth         = 0.9;   // how much is ground off the lowest knob tip (mm)

/* [Quality] */
$fn_round   = 40;          // hull spheres
$fn_rev     = 144;         // revolved cutters / knobs
profile_n   = 64;          // samples along each profile

// ---------------------------------------------------------------- geometry
phi = (1 + sqrt(5)) / 2;
// Regular dodecahedron, circumradius sqrt(3) (cube corners + 12 golden points)
verts = [
  [-1,-1,-1],[-1,-1, 1],[-1, 1,-1],[-1, 1, 1],[ 1,-1,-1],[ 1,-1, 1],[ 1, 1,-1],[ 1, 1, 1],
  [0,-1/phi,-phi],[-1/phi,-phi,0],[-phi,0,-1/phi],[0,-1/phi, phi],[-1/phi, phi,0],[-phi,0, 1/phi],
  [0, 1/phi,-phi],[ 1/phi,-phi,0],[ phi,0,-1/phi],[0, 1/phi, phi],[ 1/phi, phi,0],[ phi,0, 1/phi]];
unit_inradius = 1.3763819205;            // for circumradius sqrt(3)
face_n = [for (v = [[1,0,-phi],[-1,0,-phi],[-phi,-1,0],[-phi,1,0],[0,-phi,1],[0,-phi,-1],
                    [phi,-1,0],[-1,0,phi],[1,0,phi],[0,phi,-1],[phi,1,0],[0,phi,1]]) v / norm(v)];

// Pentagonal face of a body with inradius `ir`: in-circle radius of the face.
function face_incircle(ir) = ir / unit_inradius * 1.2360679775 * 0.6881909602;

outer_core_s  = (body_inradius - edge_round) / unit_inradius;          // scale of hull core
inner_core_s  = (body_inradius - wall - inner_round) / unit_inradius;
corner_r      = outer_core_s * sqrt(3) + edge_round;                   // centre -> rounded corner
flat_face_r   = face_incircle(body_inradius - edge_round);             // flat area of a face
ring_r_max    = flat_face_r - ring_field_margin;

function rnd(i, k) = rands(-1, 1, 1, seed * 1000 + i * 17 + k)[0] * jitter;

echo(str("corner radius (no knob) = ", corner_r, " mm; flat face in-circle = ", flat_face_r,
         " mm; ring field max radius = ", ring_r_max, " mm"));

assert(len(hole_d) == 12, "need 12 hole diameters");
for (i = [0:11]) assert(hole_d[i] / 2 + 3.5 <= ring_r_max,
                         str("hole ", i, " too large for its face"));
assert(wall - groove_depth_max >= 2.4, "grooves would thin the wall below 2.4 mm");
assert(wall >= edge_round - inner_round, "rounding radii inconsistent with wall");

module orient(n) {   // rotate +Z onto unit vector n
  rotate(a = acos(n[2]), v = [-n[1], n[0], 0]) children();
}

// ---------------------------------------------------------------- body
module outer_body() {
  hull() for (v = verts) translate(v * outer_core_s) sphere(r = edge_round, $fn = $fn_round);
}
module cavity() {
  hull() for (v = verts) translate(v * inner_core_s) sphere(r = inner_round, $fn = 24);
}

// ---------------------------------------------------------------- face relief
// Height of the face surface (relative to the face plane, + = outward) at
// radius r from the hole axis, for a hole of radius rh.  Two incised grooves
// (plus a faint third one on small holes), rounded crests, and a slightly
// raised exit so the cutter leaves the face cleanly (no coplanar faces).
function gauss(x, c, s) = exp(-pow((x - c) / s, 2));
function smooth01(x) = let(t = max(0, min(1, x))) t * t * (3 - 2 * t);
function relief(r, rh, band, dep) =
  let(u = (r - rh) / band)
  - 0.06
  - dep[0] * gauss(u, 0.40, 0.115)
  - dep[1] * gauss(u, 0.72, 0.105)
  - dep[2] * gauss(u, 0.92, 0.050)
  + 0.34 * smooth01((u - 0.80) / 0.20) * (dep[2] > 0 ? 0 : 1)
  + 0.34 * smooth01((u - 0.96) / 0.04) * (dep[2] > 0 ? 1 : 0);

// The revolved cutter for face i in face-local coordinates (z = 0 on the face
// plane, -z towards the cavity).
module face_cutter(i) {
  rh   = hole_d[i] / 2;
  band = min(ring_r_max - rh, 8.0);
  f    = hole_lip_r;
  third = band > 6.6;
  dep  = [groove_depth_max * (0.92 + 0.08 * rnd(i, 1)),
          groove_depth_max * (0.80 + 0.10 * rnd(i, 2)),
          third ? 0.30 : 0];
  zb   = -wall - 1.5;         // well inside the cavity
  zt   = 2.0;                 // well outside the face
  c    = hole_inner_chamfer;
  h0   = relief(rh + f, rh, band, dep);
  lip  = [for (k = [0:12]) let(a = 90 * k / 12)
            [rh + f - f * cos(a), h0 - f + f * sin(a)]];   // quarter round
  face = [for (k = [1:profile_n]) let(r = rh + f + (band - f) * k / profile_n)
            [r, min(relief(r, rh, band, dep), 0.34)]];
  rmax = rh + band;
  pts = concat([[0, zb], [rh + c + 0.6, zb], [rh + c + 0.6, -wall - 0.6],
                [rh, -wall + c]],
               lip, face, [[rmax, zt], [0, zt]]);
  // slight ellipticity / offset so the twelve openings are not machine-perfect
  translate([0.25 * rnd(i, 3), 0.25 * rnd(i, 4), 0])
    rotate([0, 0, 180 * rnd(i, 5)])
      scale([1 + 0.018 * rnd(i, 6), 1 - 0.018 * rnd(i, 6), 1])
        rotate_extrude($fn = $fn_rev) polygon(pts);
}

// ---------------------------------------------------------------- knobs
function smax(a, b, k) = let(h = max(k - abs(a - b), 0) / k) max(a, b) + h * h * k / 4;
function knob_profile_r(z, s) =
  let(rk = knob_r * s, a = knob_r * knob_squash * s,
      zc = knob_ball_z * s,
      ball = abs(z - zc) < a ? rk * sqrt(1 - pow((z - zc) / a, 2)) : 0,
      t = knob_neck_z * s - z,                           // depth below the neck
      flare = knob_neck_r * s
            + (knob_root_r - knob_neck_r) * s * smooth01(t / (knob_root_len * s))
            + knob_root_slope * t)
  (z > zc) ? ball : smax(ball, flare, knob_blend * s);

module knob(s) {
  a   = knob_r * knob_squash * s;
  zc  = knob_ball_z * s;
  ztop = zc + knob_flat * a;
  zbot = -6;                       // buried; the part in the cavity is cut away
  n   = profile_n * 2;
  prof = [for (k = [0:n]) let(z = zbot + (ztop - zbot) * k / n) [knob_profile_r(z, s), z]];
  rotate_extrude($fn = $fn_rev / 2)
    polygon(concat([[0, zbot]], prof, [[0, ztop]]));
}
function knob_scale(j) = 1 + 0.03 * rnd(j, 9);
function knob_tip(j) = corner_r + (knob_ball_z + knob_flat * knob_r * knob_squash) * knob_scale(j);

module knobs() {
  for (j = [0:19]) {
    d = verts[j] / norm(verts[j]);
    translate(d * corner_r) orient(d) knob(knob_scale(j));
  }
}

// ---------------------------------------------------------------- model
module dodecahedron() {
  difference() {
    union() { outer_body(); knobs(); }
    cavity();
    for (i = [0:11])
      translate(face_n[i] * body_inradius) orient(face_n[i]) face_cutter(i);
  }
}

// Print orientation: print_face points down, the model rests on flats ground
// onto the five knob tips around that face.
pn = face_n[print_face];
// support distance of knob j along pn (knob axis tilted by acos(c) from pn)
function knob_support(j, c) =
  let(s = knob_scale(j), sn = sqrt(1 - c * c),
      ztop = (knob_ball_z + knob_flat * knob_r * knob_squash) * s)
  max([for (k = [0:200]) let(z = ztop * k / 200) z * c + knob_profile_r(z, s) * sn]);
lowest = max([for (j = [0:19]) let(d = verts[j] / norm(verts[j]), c = d * pn)
                if (c > 0.5) corner_r * c + knob_support(j, c)]);
echo(str("knob-tip diameter (vertex to vertex) ~ ", 2 * knob_tip(0), " mm"));
if (print_orientation) echo(str("PRINT_CENTRE_Z = ", lowest - pad_depth));

if (print_orientation) {
  intersection() {
    translate([0, 0, lowest - pad_depth])
      rotate(a = -acos(-pn[2]), v = [pn[1], -pn[0], 0])
        dodecahedron();
    translate([-100, -100, 0]) cube(200);
  }
} else {
  dodecahedron();
}
