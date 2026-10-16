// Roman dodecahedron replica, v4 (FDM-printable).
// Modelled on photos of the Norton Disney dodecahedron (found 2023, Lincolnshire);
// an interpretation from photographs, not a scan.
//
// Build:  openscad --backend=manifold -o roman_dodecahedron_v4.stl roman_dodecahedron_v4.scad
// (OpenSCAD 2024+ "Manifold" backend recommended; CGAL also works but is slow.)
//
// Changes from v3, driven by seven reference photos (see references/SOURCES.md):
//  * Raised relief: a broad collar around each hole, then concentric rounded
//    ridges separated by narrow grooves.  The ring set is laid out from the face
//    edge inward at a fixed pitch, so the outer ring nearly reaches the edges
//    and small holes get more rings than big ones (as on the original).
//  * Knobs: almost round balls on a short neck narrower than the ball, with a
//    small fillet into the corner (v3 had thick flared roots).
//  * Crisper face edges (1.2 mm rounding instead of 2.8 mm).
//  * Hole diameters re-estimated from the photos (8.5 - 22 mm).
//
// Unchanged from v3: one revolved cutter per face runs from inside the cavity
// to outside the face, so every opening goes through the full wall.

/* [Size] */
body_inradius     = 26.0;  // centre -> outer face plane (mm). Sets overall size.
wall              = 3.0;   // face wall thickness (mm), measured to the face plane
edge_round        = 1.2;   // outer edge/corner rounding radius (mm)
inner_round       = 0.6;   // cavity edge rounding radius (mm)

/* [Openings] (one per face, all different; estimated from the photos) */
// Museum photo view (face 4 front): 8 top, 7 upper-left, 6 upper-right,
// 2 lower-left, 5 lower-right.  Dig photo view (face 9 front, opposite face 4):
// 11 top, 10 upper-left, 0 lower-left.  Faces 1 and 3 are not clearly visible
// in any photo; their sizes are guesses.
hole_d = [19.5, 10, 17, 11, 18.5, 16, 8.5, 22, 17.5, 14, 12.5, 15.5];
hole_lip_r        = 0.7;   // rounding radius of the outer hole edge
hole_inner_chamfer= 0.5;   // chamfer on the cavity side of each hole

/* [Face relief] (heights relative to the face plane) */
relief_height     = 0.38;  // top of collar and ridges
groove_depth      = 0.36;  // bottom of grooves below the face plane
groove_half_w     = 0.5;   // half width of a groove
ring_pitch        = 2.75;  // distance between grooves
outer_groove_in   = 1.6;   // outermost groove, measured in from the flat-face edge
min_collar        = 0.3;   // narrowest allowed collar between lip and first groove
max_grooves       = 3;

/* [Knobs] */
knob_r            = 3.8;   // ball radius
knob_squash       = 0.96;  // axial/lateral ratio of the ball
knob_flat         = 0.95;  // tip slightly worn flat at this fraction of the axial semi-axis
knob_ball_z       = 3.3;   // ball centre height above the corner surface
knob_neck_r       = 2.45;  // neck radius
knob_neck_z       = 0.4;   // where the root fillet starts (above corner surface)
knob_root_r       = 2.7;   // radius the root fillet tends to
knob_root_len     = 0.8;   // length of the fillet transition
knob_root_slope   = 0.12;  // extra widening per mm further into the corner
knob_blend        = 0.7;   // fillet between ball and neck

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
profile_n   = 110;         // samples along each face profile

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

function rnd(i, k) = rands(-1, 1, 1, seed * 1000 + i * 17 + k)[0] * jitter;

// Groove radii for a hole of radius rh (outermost first), only where a collar
// of at least min_collar still fits between the lip and the groove.
function groove_radii(rh, i) =
  [for (k = [0:max_grooves - 1])
     let(g = flat_face_r - outer_groove_in - k * ring_pitch + 0.12 * rnd(i, 20 + k))
     if (g - groove_half_w >= rh + hole_lip_r + min_collar) g];

echo(str("corner radius (no knob) = ", corner_r, " mm; flat face in-circle = ", flat_face_r, " mm"));
for (i = [0:11]) echo(str("face ", i, ": hole ", hole_d[i], " mm, grooves at r = ", groove_radii(hole_d[i] / 2, i)));

assert(len(hole_d) == 12, "need 12 hole diameters");
for (i = [0:11]) assert(len(groove_radii(hole_d[i] / 2, i)) >= 1,
                         str("hole ", i, " too large: no room for a ring"));
assert(wall - groove_depth >= 2.4, "grooves would thin the wall below 2.4 mm");
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
function smooth01(x) = let(t = max(0, min(1, x))) t * t * (3 - 2 * t);
function bump(x) = 1 - smooth01(abs(x));            // 1 at 0, 0 beyond |x| >= 1, smooth

// Height of the finished face surface at radius r (face-local, + = outward).
//  raised collar / ridges at +A, narrow rounded grooves down to -D, then a
//  shallow border dip just inside the flat-face edge, then a rise above the
//  face plane where the relief ends (so no coplanar faces meet in booleans).
function relief(r, gs, A, D) =
  let(re = flat_face_r)
  A
  - (A + D) * max([0, for (g = gs) bump((r - g) / groove_half_w)])
  - (A + 0.15) * smooth01((r - (re - 0.6)) / 0.55)
  + 0.45 * smooth01((r - (re - 0.05)) / 0.6);

relief_end = flat_face_r + 0.55;          // where relief() has risen to +0.3

// Face-local relief solids for face i: [additive disc, cutter].
module face_relief(i, part) {
  rh   = hole_d[i] / 2;
  gs   = groove_radii(rh, i);
  A    = relief_height * (1 + 0.08 * rnd(i, 1));
  D    = groove_depth  * (0.9 + 0.1 * rnd(i, 2));
  f    = hole_lip_r;
  c    = hole_inner_chamfer;
  r0   = rh + f;
  rs   = [for (k = [0:profile_n]) r0 + (relief_end - r0) * k / profile_n];
  // slight ellipticity / offset so the twelve openings are not machine-perfect
  translate([0.2 * rnd(i, 3), 0.2 * rnd(i, 4), 0])
    rotate([0, 0, 180 * rnd(i, 5)])
      scale([1 + 0.015 * rnd(i, 6), 1 - 0.015 * rnd(i, 6), 1])
        rotate_extrude($fn = $fn_rev)
          if (part == "add") {
            // material up to the relief surface (+0.1 overshoot, trimmed by
            // the cutter), only out to where the relief is below the face
            r_add = flat_face_r - 0.1;
            top = [for (r = rs) if (r <= r_add) [r, relief(r, gs, A, D) + 0.1]];
            polygon(concat([[rh - 0.3, -1.0], [rh - 0.3, top[0][1]]], top,
                           [[top[len(top) - 1][0], -1.0]]));
          } else {
            h0  = relief(r0, gs, A, D);
            lip = [for (k = [0:12]) let(a = 90 * k / 12) [r0 - f * cos(a), h0 - f + f * sin(a)]];
            face = [for (k = [1:profile_n]) [rs[k], relief(rs[k], gs, A, D)]];
            zb = -wall - 1.5;   // well inside the cavity
            zt = 2.0;           // well outside the face
            polygon(concat([[0, zb], [rh + c + 0.6, zb], [rh + c + 0.6, -wall - 0.6],
                            [rh, -wall + c]],
                           lip, face, [[relief_end, zt], [0, zt]]));
          }
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
            + knob_root_slope * max(t, 0))
  (z > zc) ? ball : smax(ball, flare, knob_blend * s);

module knob(s) {
  a    = knob_r * knob_squash * s;
  zc   = knob_ball_z * s;
  ztop = zc + knob_flat * a;
  zbot = -6;                       // buried; the part in the cavity is cut away
  n    = 160;
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
module on_face(i) { translate(face_n[i] * body_inradius) orient(face_n[i]) children(); }

module dodecahedron() {
  difference() {
    union() {
      outer_body();
      knobs();
      for (i = [0:11]) on_face(i) face_relief(i, "add");
    }
    cavity();
    for (i = [0:11]) on_face(i) face_relief(i, "cut");
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
