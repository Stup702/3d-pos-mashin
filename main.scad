// --- RENDER SELECTOR ---
// 0 = Exploded Assembly View
// 1 = Top Case Half (Lid)
// 2 = Bottom Case Half (Tub)
// 3 = Red Bracket (Longitudinal - Prints 2x)
// 4 = Blue Bracket (Transverse - Prints 3x)
// 5 = X-Ray Assembly (See brackets locked inside)
render_part = 0;

// --- PARAMETERS ---
// Enclosure Dimensions
enc_width = 96; // WIDENED: Increased by 6mm to reinforce the internal shear walls and prevent side blowout
wall = 3;

// Screen Dimensions
screen_w = 76;
screen_l = 121;

// Bracket Dimensions
bracket_w = 12;
bracket_t = 3;
tol = 0.5; 
bracket_depth = 10; 

// Side Profile Coordinates [Y, Z]
p1_front_bot  = [-20, 0];      
p2_front_top  = [-20, 34];     
p3_peak       = [140, 89];     
p5_foot_back  = [180, 0];      
p6_foot_front = [160, 0];      
p7_neck       = [140, 30];     

// Fastener Locations
hole_d = 3.5;              
x_offset = 41; // SHIFTED: Centered perfectly in the newly thickened side wall
y_offset = screen_l/2 + 10;  
side_y_spacing = 40;        
red_bracket_x = 25;         

// Clamshell Fastener Locations (The 4 Corner Bosses)
// SHIFTED: Moved outward to X=±40 to completely dodge the red bracket slot gouge
boss_locs = [ 
    [-40, -10],  // Front Left  (Moved 10mm forward away from screen cutout)
    [ 40, -10],  // Front Right (Moved 10mm forward away from screen cutout)
    [-40, 130],  // Back Left 
    [ 40, 130]   // Back Right
];

// --- DERIVED MATH ---
dy = p3_peak[0] - p2_front_top[0];
dz = p3_peak[1] - p2_front_top[1];
face_angle = atan2(dz, dy);
face_cy = p2_front_top[0] + (dy / 2);
face_cz = p2_front_top[1] + (dz / 2);
face_len = sqrt(dy*dy + dz*dz); // Exact diagonal length of the exterior faceplate
inner_width = enc_width - (wall * 2); // Exact internal void width
inner_face_len = face_len * ((dy - (wall * 2)) / dy); // Exact internal diagonal length

// GEOMETRY CORRECTION: Shifting the bracket deep into the case moves it backward relative to the vertical walls. 
// This calculates the exact forward shift needed to keep it perfectly centered between the inner walls.
y_corr = - (bracket_depth + (bracket_t/2)) * tan(face_angle); 

// Stepped Seam Math
cut_drop = 24; 
function get_seam_z(y) = 
    (y <= p2_front_top[0]) ? p2_front_top[1] - cut_drop :
    (y >= p3_peak[0])      ? p3_peak[1] - cut_drop :
    p2_front_top[1] - cut_drop + (y - p2_front_top[0]) * ((p3_peak[1] - p2_front_top[1]) / (p3_peak[0] - p2_front_top[0]));

// --- MODULES: BRACKETS (WITH EMBEDDED HEX POCKETS) ---
module red_bracket() {
    difference() {
        // Elegant exact fit: Over-size the bracket, then intersect it with the inverted outer shell 
        // so the ends perfectly inherit the vertical angles of the front and back walls.
        intersection() {
            cube([bracket_w, 300, bracket_t], center=true); 
            
            translate([0, 0, bracket_depth + (bracket_t/2)])
            rotate([-face_angle, 0, 0])
            translate([0, -face_cy, -face_cz])
            outer_solid();
        }
        
        // The hex pockets remain locked to the faceplate coordinates to align with clamp screws
        translate([0, y_offset, 0]) cylinder(h=15, d=6.6, center=true, $fn=6);
        translate([0, -y_offset, 0]) cylinder(h=15, d=6.6, center=true, $fn=6);
    }
}

module blue_bracket() {
    difference() {
        // Use the full exterior width so the ends sit exactly flush with the outside walls
        cube([enc_width, bracket_w, bracket_t], center=true); 
        // 6.6mm Hex Pockets for M3 Nuts
        translate([-x_offset, 0, 0]) cylinder(h=15, d=6.6, center=true, $fn=6);
        translate([ x_offset, 0, 0]) cylinder(h=15, d=6.6, center=true, $fn=6);
    }
}

// --- MODULES: SHELL COMPONENTS ---
module outer_solid() {
    rotate([90, 0, 90]) 
    linear_extrude(height=enc_width, center=true)
    polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
}

module master_shell() {
    difference() {
        union() {
            // 1. Hollow Wedge
            difference() {
                outer_solid();
                translate([0, 0, -1]) rotate([90, 0, 90]) linear_extrude(height=enc_width - (wall * 2), center=true) offset(delta=-wall) polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
                translate([0, 80, -50]) cube([enc_width + 10, 300, 100], center=true);
            }
            
            // 2. Corner Pillars
            intersection() {
                outer_solid();
                union() {
                    for(loc = boss_locs) {
                        translate([loc[0], loc[1], 0]) cylinder(h=100, d=10, $fn=30);
                    }
                }
            }

            // 3. INTERNAL CRUSH TUBES
            intersection() {
                outer_solid();
                translate([0, face_cy, face_cz])
                rotate([face_angle, 0, 0]) {
                    // Red Tubes
                    for (x = [-red_bracket_x, red_bracket_x]) {
                        for (y = [-y_offset, y_offset]) {
                            translate([x, y, -bracket_depth]) cylinder(h=100, d=10, $fn=30);
                        }
                    }
                    // Blue Tubes (Rectangular shear blocks, corrected Z-axis)
                    for (x = [-x_offset, x_offset]) {
                        for (y = [-side_y_spacing, 0, side_y_spacing]) {
                            // Centered 12x12 block extending purely upward
                            translate([x, y, -bracket_depth - bracket_t]) 
                                translate([-6, -6, 0]) cube([12, 12, 100]);
                        }
                    }
                }
            }
        }

        // --- CUTS AND DRILLS ---

        // Clamshell Corner Drills
        for(loc = boss_locs) {
            translate([loc[0], loc[1], -10]) cylinder(h=150, d=3.5, $fn=30);
        }

        // Faceplate Operations
        translate([0, face_cy, face_cz])
        rotate([face_angle, 0, 0]) {
            
            // Screen Cutout
            translate([0, 0, -bracket_depth/2 + 1]) cube([screen_w, screen_l, bracket_depth + 2], center=true);
            
            // Vertical Clamp Screws
            translate([0, 0, -20]) {
                for (x = [-red_bracket_x, red_bracket_x]) {
                    for (y = [-y_offset, y_offset]) {
                        translate([x, y, 0]) cylinder(h=100, d=hole_d, center=true, $fn=30); 
                    }
                }
                for (x = [-x_offset, x_offset]) {
                    for (y = [-side_y_spacing, 0, side_y_spacing]) {
                        translate([x, y, 0]) cylinder(h=100, d=hole_d, center=true, $fn=30); 
                    }
                }
            }

            // SLOTS: Red Brackets
            translate([0, 0, -bracket_depth - (bracket_t/2)]) {
                // Extended the cutting tool (+10) to completely blast through the outer lips
                translate([-red_bracket_x, y_corr, 0]) cube([bracket_w + tol, face_len + 10, bracket_t + tol], center=true);
                translate([ red_bracket_x, y_corr, 0]) cube([bracket_w + tol, face_len + 10, bracket_t + tol], center=true);
            }

            // SLOTS: Blue Brackets 
            translate([0, 0, -bracket_depth - bracket_t - (bracket_t/2)]) {
                for (y = [-side_y_spacing, 0, side_y_spacing]) {
                    // Extended the cutting tool (+10) to cleanly pierce the side walls
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

module case_top() {
    color("SlateGray")
    difference() {
        master_shell();
        bottom_mask();
        
        // Counterbores for Clamshell M3 screw heads
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
        intersection() {
            master_shell();
            bottom_mask();
        }
        
        // Captive Hex Nut Pockets for Clamshell Split
        for(loc = boss_locs) {
            z_cut = get_seam_z(loc[1]);
            translate([loc[0], loc[1], z_cut - 3]) 
            cylinder(h=10, d=6.6, $fn=6); 
        }
    }
}

// --- RENDER LOGIC WITH CORRECT ORIENTATION ---
rotate([0, 0, -90]) {
    if (render_part == 0) {
        translate([0, 0, 40]) case_top();
        case_bottom();
        
        translate([0, face_cy, face_cz + 40])
        rotate([face_angle, 0, 0]) {
            translate([0, 0, -bracket_depth - (bracket_t/2)]) {
                color("Crimson") translate([-red_bracket_x, 0, 0]) red_bracket();
                color("Crimson") translate([ red_bracket_x, 0, 0]) red_bracket();
            }
            translate([0, 0, -bracket_depth - bracket_t - (bracket_t/2)]) {
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
        red_bracket();
    } else if (render_part == 4) {
        blue_bracket();
    } else if (render_part == 5) {
        color("SlateGray", 1) 
        case_top();
        color("DarkSlateGray", 1) case_bottom();
        
        translate([0, face_cy, face_cz])
        rotate([face_angle, 0, 0]) {
            translate([0, 0, -bracket_depth - (bracket_t/2)]) {
                color("Crimson") translate([-red_bracket_x, 0, 0]) red_bracket();
                color("Crimson") translate([ red_bracket_x, 0, 0]) red_bracket();
            }
            translate([0, 0, -bracket_depth - bracket_t - (bracket_t/2)]) {
                for (y = [-side_y_spacing, 0, side_y_spacing]) {
                    color("DodgerBlue") translate([0, y, 0]) blue_bracket();
                }
            }
        }
    }
}