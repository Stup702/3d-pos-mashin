include <main.scad>
render_part = -1; // Disable main.scad's automatic rendering

// The top case's faceplate goes from p2_front_top to p3_peak.
// To lay the face perfectly flat on the print bed, we align it to Z=0 and flip it upside down.
rotate([180, 0, 0])
rotate([-face_angle, 0, 0])
translate([0, -p2_front_top[0], -p2_front_top[1]])
case_top();
