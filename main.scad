// --- RENDER SELECTOR ---
// 0 = Exploded Assembly View
// 1 = Top Case Half (Lid)
// 2 = Bottom Case Half (Tub)
// 3 = Blue Bracket (Transverse - Prints 3x)
// 4 = X-Ray Assembly (See brackets locked inside)
render_part = 0;

// --- PARAMETERS ---
// Enclosure Dimensions
enc_width = 100; 
wall = 3;

// Screen Dimensions
screen_w = 76;
screen_l = 121;

// Bracket Dimensions
bracket_w = 12;
bracket_t = 3;
tol = 0.5; 
bracket_depth = 14; 

// Lap Joint Parameters
lip_h = 2.0;    
lip_t = 1.5;    
lip_tol = 0.2;  

// Side Profile Coordinates [Y, Z]
p1_front_bot  = [-20, 0];      
p2_front_top  = [-20, 34];     
p3_peak       = [140, 89];     
p5_foot_back  = [180, 0];      
p6_foot_front = [160, 0];      
p7_neck       = [140, 30];     

// Fastener Locations
hole_d = 3.5;              
x_offset = 43; 
y_offset = screen_l/2 + 10;  
side_y_spacing = 40;        

front_nut_drop = 5;  // Depth of captive nut below the seam (Front)
back_nut_drop = 15;  // Depth of captive nut below the seam (Back)

// Clamshell Fastener Locations 
// SHIFTED: X moved to ±42 to permanently fuse the pillars to the inner side walls
boss_locs = [ 
    [-42, -10],  // Front Left 
    [ 42, -10],  // Front Right
    [-42, 130],  // Back Left 
    [ 42, 130]   // Back Right
];

// --- DERIVED MATH ---
dy = p3_peak[0] - p2_front_top[0];
dz = p3_peak[1] - p2_front_top[1];
face_angle = atan2(dz, dy);
face_cy = p2_front_top[0] + (dy / 2);
face_cz = p2_front_top[1] + (dz / 2);

// Stepped Seam Math
cut_drop = 24; 
function get_seam_z(y) = 
    (y <= p2_front_top[0]) ? p2_front_top[1] - cut_drop :
    (y >= p3_peak[0])      ? p3_peak[1] - cut_drop :
    p2_front_top[1] - cut_drop + (y - p2_front_top[0]) * ((p3_peak[1] - p2_front_top[1]) / (p3_peak[0] - p2_front_top[0]));

// --- MODULES: BRACKETS ---
module blue_bracket() {
    difference() {
        cube([enc_width, bracket_w, bracket_t], center=true); 
        translate([-x_offset, 0, 0]) rotate([0, 0, 30]) cylinder(h=15, d=6.6, center=true, $fn=6);
        translate([ x_offset, 0, 0]) rotate([0, 0, 30]) cylinder(h=15, d=6.6, center=true, $fn=6);
    }
}

// --- MODULES: SHELL & LAP JOINTS ---
module outer_solid() {
    rotate([90, 0, 90]) 
    linear_extrude(height=enc_width, center=true)
    polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
}

module master_shell() {
    difference() {
        union() {
            // Hollow Wedge
            difference() {
                outer_solid();
                translate([0, 0, -1]) rotate([90, 0, 90]) linear_extrude(height=enc_width - (wall * 2), center=true) offset(delta=-wall) polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
                translate([0, 80, -50]) cube([enc_width + 10, 300, 100], center=true);
            }
            
            // Corner Pillars
            intersection() {
                outer_solid();
                union() {
                    for(loc = boss_locs) {
                        translate([loc[0], loc[1], 0]) cylinder(h=100, d=10, $fn=30);
                    }
                }
            }

            // Internal Crush Tubes for Display Brackets
            intersection() {
                outer_solid();
                translate([0, face_cy, face_cz])
                rotate([face_angle, 0, 0]) {
                    for (x = [-x_offset, x_offset]) {
                        for (y = [-side_y_spacing, 0, side_y_spacing]) {
                            translate([x, y, -bracket_depth]) 
                                translate([-6, -6, 0]) cube([12, 12, 100]);
                        }
                    }
                }
            }
        }

        // Screwholes
        for(loc = boss_locs) {
            translate([loc[0], loc[1], -10]) cylinder(h=150, d=3.5, $fn=30);
        }

        // Faceplate Operations
        translate([0, face_cy, face_cz])
        rotate([face_angle, 0, 0]) {
            translate([0, 0, -bracket_depth/2 + 1]) cube([screen_w, screen_l, bracket_depth + 2], center=true);
            
            translate([0, 0, -20]) {
                for (x = [-x_offset, x_offset]) {
                    for (y = [-side_y_spacing, 0, side_y_spacing]) {
                        translate([x, y, 0]) cylinder(h=100, d=hole_d, center=true, $fn=30); 
                    }
                }
            }

            translate([0, 0, -bracket_depth - (bracket_t/2)]) {
                for (y = [-side_y_spacing, 0, side_y_spacing]) {
                    translate([0, y, 0]) cube([enc_width + 10, bracket_w + tol, bracket_t + tol], center=true);
                }
            }
        }
    }
}

// Stepped cutting mask
module bottom_mask() {
    rotate([90, 0, 90])
    linear_extrude(height=enc_width + 50, center=true)
    polygon([
        [-200, -100],
        [ 300, -100],
        [ 300, get_seam_z(300)],
        [p3_peak[0], get_seam_z(p3_peak[0])],
        [p2_front_top[0], get_seam_z(p2_front_top[0])],
        [-200, get_seam_z(-200)]
    ]);
}

// --- LAP JOINT MODULES ---
module lip_safe_positive() {
    difference() {
        intersection() {
            difference() {
                rotate([90, 0, 90]) linear_extrude(height=enc_width - lip_t*2, center=true) offset(delta=-lip_t) polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
                rotate([90, 0, 90]) linear_extrude(height=enc_width - wall*2 - 2, center=true) offset(delta=-wall) polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
            }
            translate([0, 0, lip_h]) bottom_mask();
        }
        for(loc = boss_locs) translate([loc[0], loc[1], -50]) cylinder(h=200, d=11, $fn=30);
    }
}

module lip_safe_negative() {
    difference() {
        intersection() {
            difference() {
                rotate([90, 0, 90]) linear_extrude(height=enc_width - lip_t*2 + lip_tol*2, center=true) offset(delta=-lip_t + lip_tol) polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
                rotate([90, 0, 90]) linear_extrude(height=enc_width - wall*2 - 2, center=true) offset(delta=-wall - lip_tol) polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
            }
            translate([0, 0, lip_h + 0.3]) bottom_mask();
        }
        for(loc = boss_locs) translate([loc[0], loc[1], -50]) cylinder(h=200, d=9, $fn=30);
    }
}

// --- CASE HALVES ---
module case_top() {
    color("SlateGray")
    difference() {
        master_shell();
        bottom_mask();
        lip_safe_negative(); 
        
        for(loc = boss_locs) {
            roof_z = p2_front_top[1] + (loc[1] - p2_front_top[0]) * tan(face_angle);
            translate([loc[0], loc[1], roof_z - 2]) 
            cylinder(h=20, d=6.5, $fn=30); 
        }
    }
}

module case_bottom() {
    color("DarkSlateGray")
    difference() {
        union() {
            intersection() {
                master_shell();
                bottom_mask();
            }
            lip_safe_positive(); 
        }
        
        // Side-Loading Captive Hex Nut Pockets
        for(loc = boss_locs) {
            z_cut = get_seam_z(loc[1]);
            // Apply specific drop based on front or back location
            z_drop = (loc[1] > 50) ? back_nut_drop : front_nut_drop;
            
            translate([loc[0], loc[1], z_cut - z_drop]) {
                // Pocket widened slightly for actual FDM printing tolerances
                rotate([0, 0, 30]) cylinder(h=3.2, d=6.6, center=true, $fn=6); 
                
                // Slide channel lengthened to completely blast through the inner wall
                slot_dir = (loc[0] < 0) ? 1 : -1;
                translate([slot_dir * 7.5, 0, 0]) cube([15, 6.0, 3.2], center=true);
            }
        }
    }
}

// --- RENDER LOGIC ---
rotate([0, 0, -90]) {
    if (render_part == 0) {
        translate([0, 0, 40]) case_top();
        case_bottom();
        
        translate([0, face_cy, face_cz + 40])
        rotate([face_angle, 0, 0]) {
            translate([0, 0, -bracket_depth - (bracket_t/2)]) {
                for (y = [-side_y_spacing, 0, side_y_spacing]) {
                    color("DodgerBlue") translate([0, y, 0]) blue_bracket();
                }
            }
        }
    } else if (render_part == 1) {
        case_top();
    } else if (render_part == 2) {
        case_bottom();
    } else if (render_part == 3) {
        blue_bracket();
    } else if (render_part == 4) {
        color("SlateGray", 1) 
        case_top();
        color("DarkSlateGray", 1) case_bottom();
        
        translate([0, face_cy, face_cz])
        rotate([face_angle, 0, 0]) {
            translate([0, 0, -bracket_depth - (bracket_t/2)]) {
                for (y = [-side_y_spacing, 0, side_y_spacing]) {
                    color("DodgerBlue") translate([0, y, 0]) blue_bracket();
                }
            }
        }
    }
}