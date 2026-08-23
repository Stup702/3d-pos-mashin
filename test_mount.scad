include <main.scad>

// Override render_part so main.scad doesn't render the full case
render_part = -1;

// Calculate the exact distance from the front edge to the pocket center along the sloped face
dy = face_cy - p2_front_top[0];
dz = face_cz - p2_front_top[1];
face_distance = sqrt(dy*dy + dz*dz);

// A bounding box to isolate just the screen mounting pocket
// We add 20mm padding to capture the full balcony, corner blocks, and some surrounding shell
test_box_w = screen_w + 20;
test_box_l = screen_l + 20;
test_box_h = 40; 

// Generate the flat test piece for quick 3D printing
intersection() {
    // 1. The flat top case (identical to render_part == 1 in main.scad)
    // The rotate([180,0,0]) flips it face-down, so the pocket center Y is negated.
    rotate([180, 0, 0])
    rotate([-face_angle, 0, 0])
    translate([0, -p2_front_top[0], -p2_front_top[1]])
    case_top();
    
    // 2. The isolation bounding box
    // Centered exactly on the screen pocket. 
    // Z is centered at test_box_h/2 - 5 so the box spans Z = -5 to Z = 35.
    // The faceplate skin rests exactly at Z=0, so this perfectly captures all features without clipping.
    translate([0, -face_distance, test_box_h/2 - 5]) 
    cube([test_box_w, test_box_l, test_box_h], center=true);
}
