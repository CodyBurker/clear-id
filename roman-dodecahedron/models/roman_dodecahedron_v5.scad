// Roman dodecahedron replica, v5 (FDM-printable), true 1:1 scale.
// Norton Disney dodecahedron (found 2023, Lincolnshire).  Dimensions, hole
// diameters, face lettering and ring counts follow the specialist report:
//   L. Hitchens (2023), Appendix 7 in Allen Archaeology report on the Norton
//   Disney community excavation (Archaeology Data Service, allenarc1-521355).
// Surface detail is interpreted from photographs; it is not a scan.
//
// Build:  openscad --backend=manifold -o roman_dodecahedron_v5.stl roman_dodecahedron_v5.scad
// (OpenSCAD 2024+ "Manifold" backend recommended; CGAL also works but is slow.)
//
// Changes from v4:
//  * True size: 27 mm pentagon sides (report Table 1) instead of a ~23 mm guess.
//  * The twelve hole diameters are the report's measurements, placed on faces
//    A-L following the report's face key (Fig. 2) and checked against the
//    report's photographs (see bottom_tier_reversed).  Face A (29 mm) is the base.
//  * Ring counts from the report: Face A one ring, Face J three, all others two.
//  * Knobs 9.25 mm wide projecting 8.25 mm (report: "robust and short-necked",
//    width slightly greater than projection).  v4's necks were too long.
//
// Every opening is cut by one revolved cutter running from inside the cavity
// to outside the face, so all twelve holes go through the full wall.

/* [Size] */
edge_length       = 27;    // pentagon side (report: 27 mm on all twelve faces)
body_inradius     = edge_length * 1.1135163644;  // centre -> outer face plane
wall              = 2.8;   // face wall thickness (mm), measured to the face plane.
                           // The bronze original is thinner (~1.7-2 mm, estimated
                           // from its 254 g weight); 2.8 keeps >= 2.4 mm under grooves.
edge_round        = 1.2;   // outer edge/corner rounding radius (mm)
inner_round       = 0.6;   // cavity edge rounding radius (mm)

/* [Openings] (report Table 1, by face letter) */
table_letter = ["A", "B", "C",  "D",  "E",  "F", "G", "H",  "I",  "J", "K",  "L"];
table_hole   = [ 29, 20.3, 13.4, 19.4, 20.4, 20,  27, 17.6, 17.5, 9.9, 16.2, 17];
// Face positions follow the report's key (Fig. 2): A base, B front of the base
// tier, C to its left ... F to its right; G top; H above-right of B, I
// above-left ... L.  Index i is the .scad face_n[i].
face_letter = ["C", "A", "E", "F", "K", "D", "J", "L", "G", "B", "I", "H"];
// The report's own photographs (Fig. 3 left and right views) show the 13.4 mm
// base-tier hole to the RIGHT of B and a ~20 mm hole to its left, i.e. the
// base tier runs the other way round from Fig. 2 (the top tier matches).
// true = follow the photographs (swap C<->F and D<->E positions).
bottom_tier_reversed = true;
function photo_letter(l) = !bottom_tier_reversed ? l
  : l == "C" ? "F" : l == "F" ? "C" : l == "D" ? "E" : l == "E" ? "D" : l;
function by_letter(l, table) = table[search([l], table_letter)[0]];
hole_d      = [for (l = face_letter) by_letter(photo_letter(l), table_hole)];
ring_count  = [for (l = face_letter) l == "A" ? 1 : l == "J" ? 3 : 2];  // report: A one, J three
ridge_scale = [for (l = face_letter) l == "K" ? 1.35 : 1];  // K: "particularly crisp, deep" rings
hole_lip_r        = 0.7;   // rounding radius of the outer hole edge
hole_inner_chamfer= 0.5;   // chamfer on the cavity side of each hole

/* [Face relief] (heights relative to the face plane) */
relief_height     = 0.38;  // top of collar and ridges
groove_depth      = 0.36;  // bottom of grooves below the face plane
groove_half_w     = 0.45;  // half width of a groove
ring_pitch        = 3.3;   // preferred distance between grooves
ring_pitch_min    = 1.4;   // closest allowed groove spacing (big holes)
outer_groove_in   = 1.9;   // preferred outermost groove, in from the flat-face edge
outer_margin_min  = 0.9;   // outermost groove never closer than this to the edge
min_collar        = 0.3;   // narrowest allowed collar between lip and first groove

/* [Knobs] */
knob_width        = 9.25;  // report: 9-9.5 mm
knob_projection   = 7.4;   // sharp vertex -> tip.  The report gives 8-8.5 mm,
                           // most likely from the neck base; the scale bar in the
                           // report's Fig. 3 puts the knob centres ~41 mm from the
                           // body centre, i.e. the tip ~7.4 mm beyond the vertex.
knob_r            = knob_width / 2;
knob_squash       = 0.95;  // axial/lateral ratio of the ball
knob_flat         = 0.96;  // tip slightly polished flat (report: handling polish)
knob_neck_r       = 3.4;   // short, robust neck
knob_neck_z       = 0.3;   // where the root fillet starts (above corner surface)
knob_root_r       = 3.5;   // radius the root fillet tends to
knob_root_len     = 0.6;   // length of the fillet transition
knob_root_slope   = 0.08;  // extra widening per mm further into the corner
knob_blend        = 1.0;   // fillet between ball and neck

/* [Irregularity] (small, deterministic) */
seed              = 7;
jitter            = 1.0;   // 0 = perfectly regular, 1 = default

/* [Print] */
print_orientation = true;  // rest on the five knobs around print_face
print_face        = 1;     // Face A, the report's base (largest hole)
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
sharp_vertex_r = body_inradius / unit_inradius * sqrt(3);              // unrounded corner
// ball centre above the rounded corner so the tip lands knob_projection beyond
// the sharp vertex
knob_ball_z   = sharp_vertex_r + knob_projection - corner_r
                - knob_flat * knob_r * knob_squash;

function rnd(i, k) = rands(-1, 1, 1, seed * 1000 + i * 17 + k)[0] * jitter;

// Groove radii for face i (outermost first).  ring_count[i] grooves, at the
// preferred pitch from the preferred outer position; squeezed together (and
// pushed outward, up to outer_margin_min from the edge) on big holes.
function groove_layout(i) =
  let(rh = hole_d[i] / 2, n = ring_count[i],
      lo = rh + hole_lip_r + min_collar + groove_half_w,   // innermost allowed
      g_pref = flat_face_r - outer_groove_in,
      g_max = flat_face_r - outer_margin_min,
      p_fit = n > 1 ? (g_pref - lo) / (n - 1) : 0)
  n == 1 ? [max(g_pref, min(lo, g_max)), 0]
  : p_fit >= ring_pitch     ? [g_pref, ring_pitch]
  : p_fit >= ring_pitch_min ? [g_pref, p_fit]
  : let(g0 = min(g_max, lo + (n - 1) * ring_pitch_min)) [g0, (g0 - lo) / (n - 1)];
function groove_radii(rh, i) =
  let(L = groove_layout(i))
  [for (k = [0:ring_count[i] - 1]) L[0] - k * L[1] + 0.08 * rnd(i, 20 + k)];

echo(str("corner radius (no knob) = ", corner_r, " mm; flat face in-circle = ", flat_face_r, " mm"));
for (i = [0:11]) echo(str("face ", i, " (key position ", face_letter[i], "): hole ", hole_d[i],
                         " mm, grooves at r = ", groove_radii(hole_d[i] / 2, i)));
echo(str("knob ball centre ", knob_ball_z, " mm above the rounded corner"));

assert(len(hole_d) == 12 && len(ring_count) == 12, "need 12 entries per face");
for (i = [0:11]) let(rh = hole_d[i] / 2, L = groove_layout(i), g = groove_radii(rh, i)) {
  assert(L[0] <= flat_face_r - outer_margin_min + 1e-6, str("face ", i, ": rings do not fit"));
  assert(ring_count[i] == 1 || L[1] >= 2 * groove_half_w + 0.35,
         str("face ", i, ": ridges between grooves would be thinner than 0.35 mm"));
  assert(g[len(g) - 1] - groove_half_w >= rh + hole_lip_r + 0.1,
         str("face ", i, ": no collar left around the hole"));
}
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
  A    = relief_height * ridge_scale[i] * (1 + 0.08 * rnd(i, 1));
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
