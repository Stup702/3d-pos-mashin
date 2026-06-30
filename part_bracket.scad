include <main.scad>
render_part = -1; // Disable main.scad's automatic rendering

// The bracket is natively drawn centered around Z=0 (meaning half of it is underground).
// We translate it up by half its thickness so it sits flush on the Z=0 plane.
translate([0, 0, bracket_t / 2])
blue_bracket();
