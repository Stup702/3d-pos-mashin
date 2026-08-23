// --- RENDER SELECTOR ---
// 0 = Exploded Assembly View
// 1 = Top Case Half (Lid)
// 2 = Bottom Case Half (Tub)
// 3 = X-Ray Assembly
render_part = 0;

// --- PARAMETERS ---
// Enclosure Dimensions
enc_width = 100; 
wall = 3;

// Screen Dimensions
screen_w = 75.8;
screen_l = 120.8;
screen_t = 7.3;               // total screen thickness (glass to PCB back) to sit flush
screen_hole_x_spacing = 68;
screen_hole_y_spacing = 113;
screen_boss_d = 7;            // PLACEHOLDER — verify actual boss OD with calipers before printing
screen_boss_h = 5;             // boss length per DFRobot spec
balcony_t = screen_boss_h;     // shelf thickness matched to boss length so it's fully sleeved
screen_boss_relief_clearance = 0.35;  // snug sleeve fit, not a loose pass-through — FDM tolerance only
screen_screw_clear_d = 2.8;   // M2.5 clearance hole through the corner block
corner_block_h = 4.5;         // gives the screw head a solid bearing surface below the sleeve
screen_screw_len = 10;        // M2.5 x 10mm (vs. stock M2.5 x 8mm) — gives 4.5mm block thickness and ~5.5mm of thread engagement in the boss

// Bracket Dimensions
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


// --- MODULES: PN532 SLIDER ENCLOSURE ---
module pn532_slider() {
    w = 40.5;  // Module width
    h = 42.8;  // Module height
    d = 2.3;   // Module depth (PCB + IC)
    t = 2;     // Wall thickness
    lip = 1.5; // Overhang retaining lip
    
    union() {
        // Left Rail
        translate([-(w/2 + t/2), -t/2, (d + t)/2]) cube([t, h + t, d + t], center=true);
        // Right Rail
        translate([ (w/2 + t/2), -t/2, (d + t)/2]) cube([t, h + t, d + t], center=true);
        // Bottom Stopper
        translate([0, -(h/2 + t/2), (d + t)/2]) cube([w + t*2, t, d + t], center=true);
        
        // Left Lip
        translate([-(w/2 - lip/2), -t/2, d + t/2]) cube([lip, h + t, t], center=true);
        // Right Lip
        translate([ (w/2 - lip/2), -t/2, d + t/2]) cube([lip, h + t, t], center=true);
        // Bottom Lip
        translate([0, -(h/2 - lip/2), d + t/2]) cube([w, lip, t], center=true);
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

            // Screen Mounting Pocket (Frame Walls, Balcony & Corner Blocks)
            translate([0, face_cy, face_cz])
            rotate([face_angle, 0, 0]) {
                // 1. Frame Walls (connects faceplate outer skin down to the balcony)
                translate([0, 0, -screen_t/2])
                    difference() {
                        cube([screen_w + 12, screen_l + 12, screen_t], center=true);
                        cube([screen_w, screen_l, screen_t + 2], center=true);
                    }
                    
                // 2. Balcony Plate (starts perfectly at Z = -screen_t to hold the display flush)
                translate([0, 0, -screen_t - balcony_t/2])
                    difference() {
                        cube([screen_w + 12, screen_l + 12, balcony_t], center=true);
                        cube([screen_w - 18, screen_l - 18, balcony_t + 2], center=true);
                    }
                    
                // 3. Corner Blocks (hanging directly below the balcony)
                for (x = [-screen_hole_x_spacing/2, screen_hole_x_spacing/2]) {
                    for (y = [-screen_hole_y_spacing/2, screen_hole_y_spacing/2]) {
                        translate([x, y, -screen_t - balcony_t - corner_block_h/2]) 
                            cube([12, 12, corner_block_h], center=true);
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
            // 1. Faceplate Cutout (Outer glass & screen body)
            // Cuts from Z=10 down to exactly Z=-screen_t (flush glass)
            translate([0, 0, (10 - screen_t)/2]) cube([screen_w, screen_l, 10 + screen_t], center=true);
            
            // 2. Deep cavity for components
            // Cuts from Z=-screen_t down by bracket_depth to clear all protruding components
            translate([0, 0, -screen_t - bracket_depth/2]) 
                cube([screen_w - 18, screen_l - 18, bracket_depth], center=true);
            
            // 3. Corner boss relief holes & screw clearance
            for (x = [-screen_hole_x_spacing/2, screen_hole_x_spacing/2]) {
                for (y = [-screen_hole_y_spacing/2, screen_hole_y_spacing/2]) {
                    // Snug sleeve fit for the factory boss (through the balcony)
                    translate([x, y, -screen_t - balcony_t/2]) 
                        cylinder(h=balcony_t + 2, d=screen_boss_d + screen_boss_relief_clearance, center=true, $fn=30);
                        
                    // M2.5 Clearance hole through the corner block
                    translate([x, y, -20]) 
                        cylinder(h=40, d=screen_screw_clear_d, center=true, $fn=30);
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
            
            // PN532 Slider Enclosure
            // Mounted on the inner side of the back face (Z=3 in rotated frame)
            back_dy_p = p3_peak[0] - p5_foot_back[0];
            back_dz_p = p3_peak[1] - p5_foot_back[1];
            back_angle_p = atan2(back_dz_p, back_dy_p);
            back_len_p = sqrt(back_dy_p*back_dy_p + back_dz_p*back_dz_p);
            
            translate([0, p5_foot_back[0], p5_foot_back[1]])
            rotate([back_angle_p, 0, 0])
            // Shifted slightly down the slope by 5mm to avoid the clamshell seam lip
            // True wall thickness is 3mm offset PLUS the projection of the Z=-1 hack in master_shell
            translate([0, (back_len_p / 2) - 5, 3 - cos(back_angle_p)]) 
            pn532_slider();
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
        
        // Top Lid shifted to the left
        translate([-75, 0, 0]) case_top();
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
        color("SlateGray", 1) case_top();
        color("DarkSlateGray", 1) case_bottom();
    }
}