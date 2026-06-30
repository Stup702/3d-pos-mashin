include <main.scad>
render_part = -1; // Disable main.scad's automatic rendering

// The bottom case has a sloped bottom from p1_front_bot to p7_neck
// Angle = atan2(dz, dy)
bot_angle = atan2(p7_neck[1] - p1_front_bot[1], p7_neck[0] - p1_front_bot[0]);

// Translate and rotate so the large bottom face lays perfectly flat on Z=0
rotate([-bot_angle, 0, 0])
translate([0, -p1_front_bot[0], -p1_front_bot[1]])
case_bottom();
