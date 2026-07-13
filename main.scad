// --- RENDER SELECTOR ---
// 0 = Exploded Assembly View
// 1 = Top Case Half (Lid)
// 2 = Bottom Case Half (Tub)
// 3 = U-Shaped Clamping Gasket
// 4 = X-Ray Assembly
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
p1_front_bot  = [-70, 0];      
p2_front_top  = [-70, 34];     
p3_peak       = [140, 89];     
p5_foot_back  = [180, 0];      
p6_foot_front = [160, 0];      
p7_neck       = [140, 30];     

// Fastener Locations
hole_d = 3.5;              
x_offset = 43; 
y_offset = screen_l/2 + 10;  
side_y_spacing = 40;        

// PCB Mounting Holes
pcb_x_spacing = 84;
pcb_y_spacing = 115;

front_nut_drop = 5;  // Depth of captive nut below the seam (Front)
back_nut_drop = 15;  // Depth of captive nut below the seam (Back)

// Clamshell Fastener Locations 
// SHIFTED: X moved to ±42 to permanently fuse the pillars to the inner side walls
boss_locs = [ 
    [-42, -50],  // Front Left (Moved forward to secure the new extended chin)
    [ 42, -50],  // Front Right
    [-42, 130],  // Back Left 
    [ 42, 130]   // Back Right
];

// --- DERIVED MATH ---
dy = p3_peak[0] - p2_front_top[0];
dz = p3_peak[1] - p2_front_top[1];
face_angle = atan2(dz, dy);
// Hardcoded to keep the screen horizontally aligned where it was, allocating all new space to the bottom chin.
face_cy = 60;
face_cz = p2_front_top[1] + (face_cy - p2_front_top[0]) * (dz / dy);

// Stepped Seam Math
cut_drop = 24; 
function get_seam_z(y) = 
    (y <= p2_front_top[0]) ? p2_front_top[1] - cut_drop :
    (y >= p3_peak[0])      ? p3_peak[1] - cut_drop :
    p2_front_top[1] - cut_drop + (y - p2_front_top[0]) * ((p3_peak[1] - p2_front_top[1]) / (p3_peak[0] - p2_front_top[0]));

// --- MODULES: U-SHAPED GASKET ---
module u_gasket() {
    gasket_t = 6; // 6mm thick for rigidity and to hold captive hex nuts
    
    color("DodgerBlue")
    difference() {
        union() {
            // Left Arm (Spans from X=-35 to X=-47 to safely clamp the edges of the 76mm PCB)
            translate([-41, 0, 0]) cube([12, 100, gasket_t], center=true);
            // Right Arm (Spans from X=35 to X=47)
            translate([41, 0, 0]) cube([12, 100, gasket_t], center=true);
            // Top Bridge (Connects the two arms across the top)
            translate([0, 44, 0]) cube([94, 12, gasket_t], center=true);
        }
        
        // 6x Mounting Holes & Hex Nut Pockets
        for (x = [-x_offset, x_offset]) {
            for (y = [-side_y_spacing, 0, side_y_spacing]) {
                // 3.5mm Through-hole
                translate([x, y, 0]) cylinder(h=gasket_t + 2, d=hole_d, center=true, $fn=30);
                
                // Hex nut pocket on the back side
                // Z=0 is center of 6mm thick gasket. Back face is Z=3.
                // We want a 3.2mm deep pocket, so it goes from Z=3 down to Z=-0.2.
                // Rotated by 30 degrees so the flat sides (not the sharp corners) face the thin 4mm side edges!
                translate([x, y, 3 - 3.2]) rotate([0, 0, 30]) cylinder(h=3.5, d=6.6, center=false, $fn=6);
            }
        }
    }
}

// --- MODULES: SHELL & LAP JOINTS ---
module outer_solid() {
    rotate([90, 0, 90]) 
    linear_extrude(height=enc_width, center=true)
    polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
}

// --- MODULES: SHELL & LAP JOINTS ---
module master_shell() {
    difference() {
        union() {
            // Hollow Wedge
            difference() {
                outer_solid();
                translate([0, 0, -1]) rotate([90, 0, 90]) linear_extrude(height=enc_width - (wall * 2), center=true) offset(delta=-wall) polygon([p1_front_bot, p2_front_top, p3_peak, p5_foot_back, p6_foot_front, p7_neck]);
                translate([0, 80, -50]) cube([enc_width + 10, 300, 100], center=true);
            }
            
            // Corner Pillars (Updated to Boxy & Manifold)
            intersection() {
                outer_solid();
                union() {
                    for(loc = boss_locs) {
                        // 12 wide in X, 10 deep in Y. 
                        // This intentionally penetrates the inner wall by 1mm to ensure a clean boolean union.
                        translate([loc[0], loc[1], 50]) cube([12, 10, 100], center=true);
                    }
                }
            }

            // Internal Crush Tubes for U-Gasket
            // Reduced height: The front gasket is Z=-6. We leave 1.6mm for the PCB.
            // So these tubes end at Z=-7.6 to provide a perfectly measured clamping shelf.
            intersection() {
                outer_solid();
                translate([0, face_cy, face_cz])
                rotate([face_angle, 0, 0]) {
                    for (x = [-x_offset, x_offset]) {
                        for (y = [-side_y_spacing, 0, side_y_spacing]) {
                            // Z=-7.6 is the bottom of the standoff. Cube h=100 goes UP into the faceplate.
                            translate([x, y, -7.6]) 
                                translate([-6, -6, 0]) cube([12, 12, 100]);
                        }
                    }
                }
            }

            // Screen Mounting Pocket (Frame & Standoffs)
            // Adds material to the inside of the faceplate to sink the PCB to Z=-6.
            // Spans from Z=-6 to Z=-2 (1mm overlap into the 3mm faceplate wall).
            translate([0, face_cy, face_cz])
            rotate([face_angle, 0, 0]) {
                // Rectangular Frame to deepen the cutout pocket
                translate([0, 0, -4]) cube([screen_w + 12, screen_l + 12, 4], center=true);
                
                // PCB Standoff Bosses (Square for maximum shear strength into the frame)
                for (x = [-pcb_x_spacing/2, pcb_x_spacing/2]) {
                    for (y = [-pcb_y_spacing/2, pcb_y_spacing/2]) {
                        translate([x, y, -4]) cube([10, 10, 4], center=true);
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
            // Screen Cutout
            translate([0, 0, -bracket_depth/2 + 1]) cube([screen_w, screen_l, bracket_depth + 2], center=true);
            
            // Bracket Fastener Holes & Counterbores
            for (x = [-x_offset, x_offset]) {
                for (y = [-side_y_spacing, 0, side_y_spacing]) {
                    // 3.5mm Through-hole (Shortened to prevent drilling into internal bosses)
                    translate([x, y, -15]) cylinder(h=40, d=hole_d, center=true, $fn=30); 
                    
                    // 6.5mm Counterbore (Cuts 3.2mm deep for an M3 socket head cap screw)
                    // Z=0 is the sloped surface. Translating a 20mm center-cut by 6.8 places its bottom exactly at Z = -3.2.
                    translate([x, y, 6.8]) cylinder(h=20, d=6.5, center=true, $fn=30); 
                }
            }

            // PCB Fastener Holes & Counterbores
            for (x = [-pcb_x_spacing/2, pcb_x_spacing/2]) {
                for (y = [-pcb_y_spacing/2, pcb_y_spacing/2]) {
                    // 3.5mm Through-hole (Shortened to prevent laser-beaming into the back bosses!)
                    translate([x, y, -5]) cylinder(h=20, d=hole_d, center=true, $fn=30); 
                    
                    // 6.5mm Counterbore
                    translate([x, y, 6.8]) cylinder(h=20, d=6.5, center=true, $fn=30); 
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
        
        // Uniform mask to cleanly suppress the lip around the boss without slicing it
        for(loc = boss_locs) {
            translate([loc[0], loc[1], 50]) cube([15, 10.1, 200], center=true);
        }
        
        // Expanded rear-slope cleanup: Spans Y=145 to 195 to completely swallow the diagonal wall intersection
        translate([0, 170, 50]) cube([enc_width + 10, 50, 200], center=true);
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
        
        // Matched uniform mask to ensure identical mating surfaces
        for(loc = boss_locs) {
            translate([loc[0], loc[1], 50]) cube([15, 10.1, 200], center=true);
        }
        
        // Expanded rear-slope cleanup 
        translate([0, 170, 50]) cube([enc_width + 10, 50, 200], center=true);
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
            
            // Dropped from -2 to -4.5 to bury the screw head under the downhill slope
            translate([loc[0], loc[1], roof_z - 4.5]) 
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
                // Removed rotation so flats align with the slide channel.
                // d=6.93 yields exactly 6.0mm flat-to-flat width.
                cylinder(h=3.2, d=6.93, center=true, $fn=6); 
                
                // Slide channel lengthened to completely blast through the inner wall
                slot_dir = (loc[0] < 0) ? 1 : -1;
                translate([slot_dir * 12.5, 0, 0]) cube([25, 6.0, 3.2], center=true);
            }
        }
    }
}

// --- RENDER LOGIC ---
rotate([0, 0, -90]) {
    if (render_part == 0) {
        // Bottom Tub shifted to the right
        translate([75, 0, 0]) case_bottom();
        
        // Top Lid and Brackets grouped and shifted to the left
        translate([-75, 0, 0]) {
            case_top();
            
            translate([0, face_cy, face_cz])
            rotate([face_angle, 0, 0]) {
                // The U-gasket sits directly against the Z=-7.6 crush tubes.
                // Since gasket_t=6, its center is dropped by 3mm.
                translate([0, 0, -10.6]) {
                    u_gasket();
                }
            }
        }
    } else if (render_part == 1) {
        // The top case's faceplate goes from p2_front_top to p3_peak.
        // To lay the face perfectly flat on the print bed, we align it to Z=0 and flip it upside down.
        rotate([180, 0, 0])
        rotate([-face_angle, 0, 0])
        translate([0, -p2_front_top[0], -p2_front_top[1]])
        case_top();
    } else if (render_part == 2) {
        // The natural base of the machine (from Y=-70 to Y=180) is perfectly flat on Z=0!
        // We simply translate it by -55 in Y to perfectly center its 250mm length around the origin.
        translate([0, -55, 0])
        case_bottom();
    } else if (render_part == 3) {
        // Lay U-gasket flat on bed
        translate([0, 0, 3])
        u_gasket();
    } else if (render_part == 4) {
        color("SlateGray", 1) case_top();
        color("DarkSlateGray", 1) case_bottom();
        
        translate([0, face_cy, face_cz])
        rotate([face_angle, 0, 0]) {
            translate([0, 0, -10.6]) {
                u_gasket();
            }
        }
    }
}