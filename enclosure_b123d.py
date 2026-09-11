from build123d import *
import math

# --- RENDER SELECTOR ---
# 0 = Both Halves (Exploded)
# 1 = Top Case Half (Lid)
# 2 = Bottom Case Half (Tub)
# 3 = Assembled Casing
render_part = 0

# --- PARAMETERS ---
enc_width = 100.0 
wall = 4.0
corner_r = 4.0
base_chamfer = 1.5

# Screen Dimensions (DFRobot 5" DFR0550-V2)
screen_w = 75.8
screen_l = 120.8
screen_t = 7.8               # 7.8mm drop depth for flush glass fit
screen_ribbon_gap = 1.5      # 1.5mm ribbon clearance channel
screen_hole_x_spacing = 68.0
screen_hole_y_spacing = 113.0
screen_boss_d = 5.5          # Factory brass standoff diameter
screen_boss_h = 5.0          # Standoff length
balcony_t = screen_boss_h     # 5.0mm shelf thickness to fully sleeve the standoff
screen_boss_relief_clearance = 0.50 # 6.00mm sleeve hole diameter
screen_screw_clear_d = 3.0   # M2.5 screw clearance
corner_block_h = 4.5         # Solid bearing block for screw head
bracket_depth = 14.0         # Component clearance cavity

# Profile Coordinates [Y, Z]
p1 = (-70.0, 0.0)      
p2 = (-70.0, 34.0)     
p3 = (140.0, 89.0)     
p5 = (180.0, 0.0)      
p6 = (160.0, 0.0)      
p7 = (140.0, 30.0)

# Sloped Face Geometry
dy = p3[0] - p2[0]  # 210.0
dz = p3[1] - p2[1]  # 55.0
face_angle = math.atan2(dz, dy) # 14.676 deg
roof_angle = math.atan2(p3[1] - p5[1], p5[0] - p3[0])
face_cy = 60.0
face_cz = p2[1] + (face_cy - p2[0]) * (dz / dy) # 68.0476 mm

# Screen Coordinate Plane:
screen_plane = Plane(
    origin=(0, face_cy, face_cz),
    x_dir=(1, 0, 0),
    z_dir=(0, -math.sin(face_angle), math.cos(face_angle))
)

# Clamshell Fastener Locations [X, Y]
boss_locs = [ 
    (-42.0, -50.0),
    ( 42.0, -50.0),
    (-42.0, 130.0),
    ( 42.0, 130.0)
]

front_nut_drop = 5.0
back_nut_drop  = 15.0
cut_drop = 24.0

def get_seam_z(y):
    if y <= p2[0]:
        return p2[1] - cut_drop
    elif y >= p3[0]:
        return p3[1] - cut_drop - (y - p3[0]) * math.tan(roof_angle)
    else:
        return p2[1] - cut_drop + (y - p2[0]) * (dz / dy)

# Lap Joint Parameters
lip_h = 2.0
lip_t = 1.8
lip_tol = 0.2

print("Generating full POS terminal enclosure with build123d...")

# ==========================================
# 1. BUILD MASTER SHELL
# ==========================================
with BuildPart() as master:
    # A. Outer Extrusion
    with BuildSketch(Plane.YZ):
        Polygon([p1, p2, p3, p5, p6, p7])
    extrude(amount=enc_width / 2, both=True)
    
    # B. 4.0mm Vertical Corner Fillets
    front_vert = master.edges().filter_by(Axis.Z).filter_by_position(Axis.Y, -71, -69)
    if front_vert:
        fillet(front_vert, radius=corner_r)

    # C. 1.5mm Bottom Base Chamfer
    bottom_edges = master.edges().filter_by_position(Axis.Z, -0.1, 0.1)
    bottom_perimeter = [e for e in bottom_edges if abs(abs(e.center().X) - enc_width/2) < 1.0 or e.center().Y < -65 or e.center().Y > 175]
    if bottom_perimeter:
        try:
            chamfer(bottom_perimeter, length=base_chamfer)
        except Exception as e:
            print("Chamfer note:", e)

    # SAVE OUTER SOLID BOUNDARY FOR TRIMMING PILLARS:
    outer_solid_boundary = master.part

    # D. Hollow Wedge (3.5mm Heavy Duty Walls)
    with BuildSketch(Plane.YZ):
        offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-wall, kind=Kind.INTERSECTION)
    inner_cavity = extrude(amount=(enc_width - 2 * wall) / 2, both=True, mode=Mode.PRIVATE)
    master.part = master.part - inner_cavity

    # E. Corner Screw Boss Pillars (12x10 solid columns, strictly trimmed inside outer skin)
    with BuildPart(mode=Mode.PRIVATE) as pillar_builder:
        for bx, by in boss_locs:
            with BuildSketch(Plane.XY.offset(100)):
                with Locations((bx, by)):
                    Rectangle(12, 10)
            extrude(amount=-150)
    contained_pillars = pillar_builder.part & outer_solid_boundary
    master.part = master.part + contained_pillars

    # F. Screen Mounting Frame & Pocket (on the Screen Plane)
    with BuildSketch(screen_plane.offset(-screen_t / 2)):
        Rectangle(screen_w + 12, screen_l + 12)
        with Locations((screen_ribbon_gap / 2, 0)):
            Rectangle(screen_w + screen_ribbon_gap + 0.4, screen_l + 0.4, mode=Mode.SUBTRACT)
    extrude(amount=screen_t / 2, both=True, mode=Mode.ADD)

    # Balcony Plate (at Z = -screen_t to hold the display flush)
    with BuildSketch(screen_plane.offset(-screen_t - balcony_t / 2)):
        Rectangle(screen_w + 12, screen_l + 12)
        Rectangle(screen_w - 18, screen_l - 18, mode=Mode.SUBTRACT)
    extrude(amount=balcony_t / 2, both=True, mode=Mode.ADD)

    # Corner Mounting Blocks (below the balcony)
    for hx in [-screen_hole_x_spacing / 2, screen_hole_x_spacing / 2]:
        for hy in [-screen_hole_y_spacing / 2, screen_hole_y_spacing / 2]:
            with BuildSketch(screen_plane.offset(-screen_t - balcony_t - corner_block_h / 2)):
                with Locations((hx, hy)):
                    Rectangle(12, 12)
            extrude(amount=corner_block_h / 2, both=True, mode=Mode.ADD)

    # Faceplate Viewing Cutout (punches through outer skin)
    with BuildSketch(screen_plane.offset(3)):
        with Locations((screen_ribbon_gap / 2, 0)):
            Rectangle(screen_w + screen_ribbon_gap, screen_l)
    extrude(amount=7, both=True, mode=Mode.SUBTRACT)

    # Deep Component Clearance Cavity
    with BuildSketch(screen_plane.offset(-screen_t - bracket_depth / 2)):
        Rectangle(screen_w - 18, screen_l - 18)
    extrude(amount=bracket_depth / 2, both=True, mode=Mode.SUBTRACT)

    # Boss Sleeves & M2.5 Screw Holes
    for hx in [-screen_hole_x_spacing / 2, screen_hole_x_spacing / 2]:
        for hy in [-screen_hole_y_spacing / 2, screen_hole_y_spacing / 2]:
            with BuildSketch(screen_plane.offset(-screen_t - balcony_t / 2)):
                with Locations((hx, hy)):
                    Circle(radius=(screen_boss_d + screen_boss_relief_clearance) / 2)
            extrude(amount=(balcony_t + 2) / 2, both=True, mode=Mode.SUBTRACT)
            
            with BuildSketch(screen_plane.offset(-20)):
                with Locations((hx, hy)):
                    Circle(radius=screen_screw_clear_d / 2)
            extrude(amount=20, both=True, mode=Mode.SUBTRACT)

    # DSI Ribbon Cable Pass-Through Notch on Front Chin Balcony (-Y)
    # Allows 15-pin FPC cable from screen DSI connector to pass through balcony
    dsi_notch_w = 22.0
    dsi_notch_l = 16.0
    with BuildSketch(screen_plane.offset(-screen_t - balcony_t / 2)):
        with Locations((0.0, -56.0)):
            Rectangle(dsi_notch_w, dsi_notch_l)
    extrude(amount=(balcony_t + 2) / 2, both=True, mode=Mode.SUBTRACT)

master_shell_part = master.part

# ==========================================
# 2. CUTTER FOR CLAMSHELL SPLIT
# ==========================================
# Entire rear back panel (Y >= 140) belongs to the bottom tub!
with BuildPart() as split_cutter:
    with BuildSketch(Plane.YZ):
        Polygon([
            (-200.0, -100.0),
            ( 300.0, -100.0),
            ( 300.0,  150.0),             # Keeps all Y >= 140 in case_bottom
            (p3[0],   150.0),             # Vertical seam at the peak Y=140
            (p3[0],   get_seam_z(p3[0])), # Drops to side seam Z=65
            (p2[0],   get_seam_z(p2[0])), # Front chin seam Z=10
            (-200.0,  get_seam_z(-200.0))
        ])
    extrude(amount=enc_width + 50, both=True)

bottom_mask_solid = split_cutter.part

# ==========================================
# 3. INTERLOCKING LAP JOINTS
# ==========================================
with BuildPart() as pos_lip:
    # Outer lip solid with concentric corner fillet matching outer shell
    with BuildPart() as pos_outer_builder:
        with BuildSketch(Plane.YZ):
            offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-lip_t)
        extrude(amount=(enc_width - 2 * lip_t) / 2, both=True)
        r_pos = corner_r - lip_t
        if r_pos > 0.1:
            v_edges = pos_outer_builder.edges().filter_by(Axis.Z).filter_by_position(Axis.Y, -70, -66)
            if v_edges:
                fillet(v_edges, radius=r_pos)
    outer_lip_ext = pos_outer_builder.part
    
    with BuildSketch(Plane.YZ):
        offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-wall)
    inner_lip_ext = extrude(amount=(enc_width - 2 * wall - 2) / 2, both=True, mode=Mode.PRIVATE)
    
    lip_ribbon = outer_lip_ext - inner_lip_ext
    
    # Intersect with bottom_mask shifted up by lip_h
    lip_positive = lip_ribbon & (bottom_mask_solid.moved(Location((0, 0, lip_h))))
    
    # Suppress around boss pillars and rear slope
    with BuildPart() as masks:
        for bx, by in boss_locs:
            with BuildSketch(Plane.XY.offset(50)):
                with Locations((bx, by)):
                    Rectangle(25, 25)
            extrude(amount=-100)
        with BuildSketch(Plane.XY.offset(50)):
            with Locations((0, 170)):
                Rectangle(enc_width + 10, 50)
        extrude(amount=-100)
        # Suppress lip joint at power button slot (Right wall, Y = 32.0, X = 50.0)
        with BuildSketch(Plane.XY.offset(50)):
            with Locations((48.0, 32.0)):
                Rectangle(15.0, 20.0)
        extrude(amount=-100)
        
    lip_positive = lip_positive - masks.part

lip_positive_solid = lip_positive

with BuildPart() as neg_lip:
    # Outer negative cutter with concentric corner fillet matching outer shell
    with BuildPart() as neg_outer_builder:
        with BuildSketch(Plane.YZ):
            offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-lip_t + lip_tol)
        extrude(amount=(enc_width - 2 * lip_t + 2 * lip_tol) / 2, both=True)
        r_neg = corner_r - lip_t + lip_tol
        if r_neg > 0.1:
            v_edges_neg = neg_outer_builder.edges().filter_by(Axis.Z).filter_by_position(Axis.Y, -70, -66)
            if v_edges_neg:
                fillet(v_edges_neg, radius=r_neg)
    outer_neg_ext = neg_outer_builder.part
    
    with BuildSketch(Plane.YZ):
        offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-wall - lip_tol)
    inner_neg_ext = extrude(amount=(enc_width - 2 * wall - 2) / 2, both=True, mode=Mode.PRIVATE)
    
    neg_ribbon = outer_neg_ext - inner_neg_ext
    lip_negative = neg_ribbon & (bottom_mask_solid.moved(Location((0, 0, lip_h + 0.3))))
    
    with BuildPart() as masks:
        for bx, by in boss_locs:
            with BuildSketch(Plane.XY.offset(50)):
                with Locations((bx, by)):
                    Rectangle(25, 25)
            extrude(amount=-100)
        with BuildSketch(Plane.XY.offset(50)):
            with Locations((0, 170)):
                Rectangle(enc_width + 10, 50)
        extrude(amount=-100)
        # Suppress lip joint at power button slot (Right wall, Y = 32.0, X = 50.0)
        with BuildSketch(Plane.XY.offset(50)):
            with Locations((48.0, 32.0)):
                Rectangle(15.0, 20.0)
        extrude(amount=-100)
        
    lip_negative = lip_negative - masks.part

lip_negative_solid = lip_negative

# ==========================================
# 4. PN532 SLIDER MODULE
# ==========================================
def build_pn532_slider():
    w = 41.5
    h = 42.8
    d = 3.3
    t = 2.0
    lip = 1.5
    with BuildPart() as slider:
        with BuildSketch():
            # Rails & Bottom Stopper
            with Locations((-(w/2 + t/2), -t/2)):
                Rectangle(t, h + t)
            with Locations(((w/2 + t/2), -t/2)):
                Rectangle(t, h + t)
            with Locations((0, -(h/2 + t/2))):
                Rectangle(w + t*2, t)
        extrude(amount=d + t)
        # Retaining lips
        with BuildSketch(Plane.XY.offset(d)):
            with Locations((-(w/2 - lip/2), -t/2)):
                Rectangle(lip, h + t)
            with Locations(((w/2 - lip/2), -t/2)):
                Rectangle(lip, h + t)
            with Locations((0, -(h/2 - lip/2))):
                Rectangle(w, lip)
        extrude(amount=t)
    return slider.part

# ==========================================
# 5. CASE TOP & CASE BOTTOM HALVES
# ==========================================
# Top Lid (Clean, seamless faceplate with zero screw holes)
case_top = (master_shell_part - bottom_mask_solid) - lip_negative_solid

# Blind Heat-Set Insert Holes in Top Lid (M3 x 4mm insert: hole diameter 3.8mm, depth 6.5mm)
# Starts 3.0mm below z_cut to penetrate the full sloped boss face -> 100% round circular hole!
insert_hole_d = 3.8 # Sized smaller than M3 brass insert knurl OD (4.2mm) for strong plastic grip
insert_chamfer_d = 4.1
with BuildPart() as insert_holes:
    for bx, by in boss_locs:
        z_cut = get_seam_z(by)
        # Blind cylindrical hole drilled UPWARDS from below the parting seam into the boss
        with BuildSketch(Plane.XY.offset(z_cut - 3.0)):
            with Locations((bx, by)):
                Circle(radius=insert_hole_d / 2)
        extrude(amount=9.6)
        # 45 deg lead-in chamfer for easy alignment when pressing with soldering iron
        with BuildSketch(Plane.XY.offset(z_cut - 3.0)):
            with Locations((bx, by)):
                Circle(radius=insert_chamfer_d / 2)
        extrude(amount=3.6)
case_top = case_top - insert_holes.part

# Bottom Tub
case_bottom = (master_shell_part & bottom_mask_solid) + lip_positive_solid

# Add PN532 Slider inside bottom tub
back_dy = p3[0] - p5[0]
back_dz = p3[1] - p5[1]
back_angle = math.atan2(back_dz, back_dy)
back_len = math.sqrt(back_dy**2 + back_dz**2)

slider_solid = build_pn532_slider()
slider_located = slider_solid.moved(
    Location((0, (back_len / 2) - 5, 3 - math.cos(back_angle)))
).moved(
    Location((0, 0, 0), (1, 0, 0), math.degrees(back_angle))
).moved(
    Location((0, p5[0], p5[1]))
)
case_bottom = case_bottom + slider_located

# Bottom-Entry Screwholes (screws inserted from desk base underneath)
with BuildPart() as bottom_screw_holes:
    for bx, by in boss_locs:
        z_cut = get_seam_z(by)
        # M3 screw clearance hole (3.4mm diameter) all the way through to parting seam
        with BuildSketch(Plane.XY.offset(-1)):
            with Locations((bx, by)):
                Circle(radius=3.4 / 2)
        extrude(amount=z_cut + 5)
        
        # Recessed counterbore from the desk base (Z = 0)
        # Front: 3.5mm deep (flange = 11.7mm, M3x16 reaches 4.3mm into insert)
        # Back: 50.5mm deep (flange = 11.9mm, M3x16 reaches 4.1mm into insert)
        cb_depth = 50.5 if by > 50 else 3.5
        with BuildSketch(Plane.XY.offset(-1)):
            with Locations((bx, by)):
                Circle(radius=6.5 / 2)
        extrude(amount=cb_depth + 1)
case_bottom = case_bottom - bottom_screw_holes.part

# ==========================================
# 5B. CONFORMAL INTERNAL CRADLES & FAN (SLANTED FLOOR)
# ==========================================
# The underbelly floor slopes from p1=(-70, 0) to p7=(140, 30) at angle ~8.13 deg.
# To prevent any floating geometry, we construct a conformal floor Plane on the inner floor face.
floor_dy = p7[0] - p1[0]
floor_dz = p7[1] - p1[1]
floor_angle = math.atan2(floor_dz, floor_dy)
floor_ny = -math.sin(floor_angle)
floor_nz = math.cos(floor_angle)

# Inner floor point at Y = 0:
floor_z_outer_0 = (0 - p1[0]) * (floor_dz / floor_dy)
inner_floor_origin = (0, wall * floor_ny, floor_z_outer_0 + wall * floor_nz)

floor_plane = Plane(
    origin=inner_floor_origin,
    x_dir=(1, 0, 0),
    z_dir=(0, floor_ny, floor_nz) # Normal points inward into the tub cavity
)

# --- 1. UPS Board Cradle (Front Chin Section) ---
# Board size: 56.20mm (along Y/wall) x 79.08mm (along X)
# Height: 3.5mm standoff pedestal + 1.6mm PCB friction lip = 5.1mm total wall height
ups_w = 78.30
ups_l = 55.50
# +1.0mm give on top (+Y) and right (+X) to eliminate painful friction fit.
# Left (-X) stop and front (-Y) stop remain fixed for DC barrel jack and chin alignment.
ups_give_x = 1.0 # extra clearance on +X (right side)
ups_give_y = 1.0 # extra clearance on +Y (top/fan side)
ups_tol = 0.6    # base bilateral tolerance (0.3mm per side)
ups_wall = 1.5
ups_pedestal_h = 3.5
ups_pcb_t = 1.6
ups_total_h = ups_pedestal_h + ups_pcb_t # 5.1mm

# Base coordinates: fixed left stop at X = -44.50, fixed front stop at Y = -44.05
# With +1.0mm on right and +1.0mm on top:
# Pocket spans: X in [-44.50, +35.40] (width = 79.90), Y in [-44.05, +13.05] (length = 57.10)
ups_pocket_w = ups_w + ups_tol + ups_give_x # 79.90 mm
ups_pocket_l = ups_l + ups_tol + ups_give_y # 57.10 mm
ups_cx = -4.55       # Center shifted +0.5mm in X
ups_cy_local = -15.50 # Center shifted +0.5mm in Y

# 4mm screw hole boss: 39.7mm from left wall, 18.9mm from fan-side (top/rear) edge
# Referenced to FIXED PCB datum:
# PCB left edge is at X = -44.20, hole is at -44.20 + 39.70 = -4.50 mm
# PCB rear edge is at Y = +11.75, hole is at +11.75 - 18.90 = -7.15 mm
ups_boss_x = -4.50    # Unaltered: locks PCB to fixed datum & DC port
ups_boss_y = -7.15    # Unaltered: locks PCB to fixed datum & DC port
ups_boss_outer_d = 8.0
ups_pin_d = 3.45 # Reduced from 3.70mm to 3.45mm for smooth, painless drop-in without FDM pin binding
ups_pin_h = 4.00 # 4.0mm pole height (protrudes 2.4mm above 1.6mm PCB for hot glue gun adhesion)

# DC Barrel Jack Port Position on Left Wall (X = -50)
# Measured: 18mm from fan/bat rear edge, 9mm width -> center Y = -10.75mm
# Height: 3.5mm pedestal + 1.6mm PCB + 3.0mm bottom margin + 3.65/2 = 9.925mm above floor
jack_rear_edge_y = -16.0 + (ups_l / 2.0) # +11.75 mm (nominal PCB rear edge)
jack_local_y = jack_rear_edge_y - 18.0 - 4.5    # -10.75 mm
jack_z = ups_pedestal_h + ups_pcb_t + 3.0 + 3.65 / 2.0 # 9.925 mm
jack_world_pt = floor_plane.from_local_coords((ups_cx, jack_local_y, jack_z))

with BuildPart() as ups_cradle:
    # A. Center Locating Pedestal & Pole (3.5mm shoulder + 4.0mm pole into PCB 4mm hole)
    # Completely eliminates screws and screwdrivers near delicate chips!
    with BuildSketch(floor_plane):
        with Locations((ups_boss_x, ups_boss_y)):
            Circle(radius=ups_boss_outer_d / 2)
    extrude(amount=ups_pedestal_h)

    # Locating pole: 3.2mm cylinder + 0.8mm conical lead-in tip (taper=45) for self-centering pilot action
    with BuildSketch(floor_plane.offset(ups_pedestal_h)):
        with Locations((ups_boss_x, ups_boss_y)):
            Circle(radius=ups_pin_d / 2)
    extrude(amount=ups_pin_h - 0.8)

    with BuildSketch(floor_plane.offset(ups_pedestal_h + ups_pin_h - 0.8)):
        with Locations((ups_boss_x, ups_boss_y)):
            Circle(radius=ups_pin_d / 2)
    extrude(amount=0.8, taper=45)

    # B. Friction-Free Perimeter Wall (5.1mm tall) with +1mm give on top and right
    with BuildSketch(floor_plane):
        with Locations((ups_cx, ups_cy_local)):
            Rectangle(ups_pocket_w + 2 * ups_wall, ups_pocket_l + 2 * ups_wall)
            Rectangle(ups_pocket_w, ups_pocket_l, mode=Mode.SUBTRACT)
    extrude(amount=ups_total_h)

    # C. Open Cable Bay in Upper-Right Corner (Fan-Side Rear + Right Side)
    # Replaces the upper-right corner of the wall with an open cable routing bay
    # Widened toward -X by 10.0mm (reduces top wall length by another centimeter!)
    # Spans from X = +3.0mm to +43.0mm, and Y = -7.0mm to +16.0mm, flush to inner floor!
    corner_cut_w = 40.0
    corner_cut_l = 23.0
    corner_cut_cx = 23.0
    corner_cut_cy = 4.5
    with BuildSketch(floor_plane.offset(-2.0)):
        with Locations((corner_cut_cx, corner_cut_cy)):
            Rectangle(corner_cut_w, corner_cut_l)
    extrude(amount=ups_total_h + 4.0, mode=Mode.SUBTRACT)

    # D. Left-side wall (-X) notch for square DC barrel jack body:
    # Starts at ups_total_h (5.1mm) to match the UPS perimeter wall height and PCB top surface!
    # Conceals the 1.6mm raw PCB edge and blocks the view underneath the PCB completely.
    ups_left_wall_cx = ups_cx - (ups_pocket_w + ups_wall) / 2.0
    ups_jack_notch_w = 12.0
    with BuildSketch(floor_plane.offset(ups_total_h)):
        with Locations((ups_left_wall_cx, jack_local_y)):
            Rectangle(ups_wall * 4.0, ups_jack_notch_w)
    extrude(amount=ups_total_h + 4.0, mode=Mode.SUBTRACT)

    # E. 3 Corner Support Pads (3.5mm tall) to keep PCB perfectly level
    # Top-right (+X, +Y) pad is omitted so no standalone pillar obstructs cables!
    # Quad-point support: 3 corner pads + large central boss shoulder form an unshakeable support plane.
    pad_size = 5.0
    pad_coords = [
        (-ups_pocket_w / 2 + pad_size / 2, -ups_pocket_l / 2 + pad_size / 2), # Bottom-Left (-X, -Y)
        ( ups_pocket_w / 2 - pad_size / 2, -ups_pocket_l / 2 + pad_size / 2), # Bottom-Right (+X, -Y)
        (-ups_pocket_w / 2 + pad_size / 2,  ups_pocket_l / 2 - pad_size / 2)  # Top-Left (-X, +Y)
    ]
    with BuildSketch(floor_plane):
        for px, py in pad_coords:
            with Locations((ups_cx + px, ups_cy_local + py)):
                Rectangle(pad_size, pad_size)
    extrude(amount=ups_pedestal_h)

case_bottom = case_bottom + ups_cradle.part

# Open Port on Case Left Wall:
# Starts at floor_plane.offset(ups_total_h) so that a solid 5.1mm threshold / half-wall
# is retained at the outer wall, flush with the UPS perimeter walls and top of the PCB!
with BuildPart() as dc_jack_port:
    with BuildSketch(floor_plane.offset(ups_total_h)):
        with Locations((-47.5, jack_local_y)):
            Rectangle(25.0, 12.0)
    extrude(amount=16.0)
case_bottom = case_bottom - dc_jack_port.part
case_top = case_top - dc_jack_port.part

# --- 2. Cooling Fan Slot & Vents (Middle Section: LD3007MS 30mm Pi-FAN) ---
# Spec: LD3007MS, 30mm square x 7mm, 24mm x 24mm mounting hole spacing
# Shifted back to local y = 48.0: opens 19.1mm front corridor for UPS USB-C cord,
# and aligns intake airflow right in front of the Raspberry Pi 4 CPU!
fan_size = 30.0
fan_hole_spacing = 24.0
fan_cx = 0.0
fan_cy_local = 48.0
fan_standoff_h = 2.0
fan_standoff_d = 5.5

# Fasteners: 2.3mm screws (14mm length) inserted from the underside, tightening into hex nuts on top
fan_screw_d = 2.3
fan_hole_d = 2.6   # 2.6mm clearance hole (compensated for FDM 3D print shrinkage)
fan_cb_d = 5.2     # 5.2mm underbelly counterbore for 4.2-4.4mm pan/button heads
fan_cb_depth = 1.5 # 1.5mm deep into 3.5mm floor -> leaves 2.0mm solid floor flange
# Stack: 2.0mm floor flange + 2.0mm standoff + 7.0mm fan = 11.0mm clamped
# 14.0mm screw reaches 3.0mm above fan, providing full thread grip for the ~1.8mm hex nut!

with BuildPart() as fan_mount:
    # 4 Corner Standoffs (2.0mm tall) on the inner floor
    with BuildSketch(floor_plane):
        for fx in [-fan_hole_spacing / 2, fan_hole_spacing / 2]:
            for fy in [-fan_hole_spacing / 2, fan_hole_spacing / 2]:
                with Locations((fan_cx + fx, fan_cy_local + fy)):
                    Circle(radius=fan_standoff_d / 2)
    extrude(amount=fan_standoff_h)
case_bottom = case_bottom + fan_mount.part

# Fan Air Intake Vent, Screw Clearance Holes & Underbelly Counterbores through the Slanted Bottom Floor
with BuildPart() as fan_vents:
    # 1. 4 Corner Screw Through-Holes (cut through both the 3.5mm floor AND the 2.0mm standoffs!)
    with BuildSketch(floor_plane):
        for fx in [-fan_hole_spacing / 2, fan_hole_spacing / 2]:
            for fy in [-fan_hole_spacing / 2, fan_hole_spacing / 2]:
                with Locations((fan_cx + fx, fan_cy_local + fy)):
                    Circle(radius=fan_hole_d / 2)
    extrude(amount=10.0, both=True)

    # 2. 4 Underbelly Counterbores on the outside underbelly floor
    # Cut from outer face (offset -wall - 0.1) inward by fan_cb_depth + 0.1
    with BuildSketch(floor_plane.offset(-wall - 0.1)):
        for fx in [-fan_hole_spacing / 2, fan_hole_spacing / 2]:
            for fy in [-fan_hole_spacing / 2, fan_hole_spacing / 2]:
                with Locations((fan_cx + fx, fan_cy_local + fy)):
                    Circle(radius=fan_cb_d / 2)
    extrude(amount=fan_cb_depth + 0.1)

    # 3. Air Intake Vent Slots (cut through the 3.5mm floor outwards)
    with BuildSketch(floor_plane):
        with Locations((fan_cx, fan_cy_local)):
            for i in range(-2, 3):
                with Locations((0, i * 4.0)):
                    slot_w = math.sqrt(max(0, 12.0**2 - (i * 4.0)**2)) * 2 - 2
                    if slot_w > 3:
                        Rectangle(slot_w, 2.2)
    extrude(amount=-10.0)
case_bottom = case_bottom - fan_vents.part

# --- 3. Battery Pack Cradle (Rear Section, Pushed Back to Floor Drop) ---
# Pack size: 67.25mm (along X) x 73.15mm (along Y) x 18.38mm
# Sits cleanly between the rear boss pillars (72.0mm gap vs 70.85mm cradle outer width = 0.58mm clearance on each side!)
# Pushed back to bat_cy_local = 104.5: takes full advantage of the straightened inner floor drop (Y = 143.6mm),
# ending at local y = 142.9mm with 0.7mm safety margin before the drop.
bat_w = 67.80
bat_l = 73.35
bat_tol = 0.6
bat_wall = 1.5
bat_h = 10.0 # 10.0mm heavy-duty retention perimeter wall
bat_cx = 0.0
bat_cy_local = 104.5

with BuildPart() as bat_cradle:
    with BuildSketch(floor_plane):
        with Locations((bat_cx, bat_cy_local)):
            Rectangle(bat_w + bat_tol + 2 * bat_wall, bat_l + bat_tol + 2 * bat_wall)
            Rectangle(bat_w + bat_tol, bat_l + bat_tol, mode=Mode.SUBTRACT)
    extrude(amount=bat_h)
case_bottom = case_bottom + bat_cradle.part

# --- 4. Right-Wall Momentary Power Button System (Option A: Drop-in T-Plunger with Full Fat Nib) ---
# Location: Right wall (X_outer = +50.0mm, X_inner = +45.5mm), Y = +32.0mm, Z = 28.0mm
btn_x = 50.0
btn_y = 32.0
btn_z = 28.0
btn_seam_z = get_seam_z(btn_y) # 36.714 mm

# T-Plunger Dimensions
plunger_cap_d = 5.8
plunger_cap_l = 2.3
plunger_flange_d = 8.6
plunger_flange_t = 1.5
plunger_nib_d = 4.8  # Full Fat Nib (380% dome contact area, 0.8mm concentric radial margin)
plunger_nib_l = 1.1

# Plunger Solid (modeled in resting position, ready to slice horizontally)
with BuildPart() as plunger_builder:
    # 1. Outer Button Cap (protrudes 0.8mm proud of wall at rest)
    with Locations((btn_x + 0.8 - plunger_cap_l / 2, btn_y, btn_z)):
        Cylinder(radius=plunger_cap_d / 2, height=plunger_cap_l, rotation=(0, 90, 0))
    # 2. Retention Flange (rests against wall stop at X = 48.5)
    with Locations((48.5 - plunger_flange_t / 2, btn_y, btn_z)):
        Cylinder(radius=plunger_flange_d / 2, height=plunger_flange_t, rotation=(0, 90, 0))
    # 3. Full Fat Nib (pushes against switch dome)
    with Locations((47.0 - plunger_nib_l / 2, btn_y, btn_z)):
        Cylinder(radius=plunger_nib_d / 2, height=plunger_nib_l, rotation=(0, 90, 0))
    # 4. Flat bed contact facet (0.45mm shaved off bottom along Z for PEI bed adhesion)
    with Locations((btn_x, btn_y, btn_z - plunger_flange_d / 2 + 0.45 / 2)):
        Box(20.0, 15.0, 0.45, mode=Mode.SUBTRACT)

button_plunger = plunger_builder.part

# Drop-in Keystone Retaining Clip (Fills gap above button, locks plunger & switch)
tol_y = 0.30
tol_x = 0.15
with BuildPart() as keystone_builder:
    # 1. Outer Cap Plug (Segment 1)
    with Locations((49.25, btn_y, 35.0)):
        Box(1.5 - tol_x, 6.4 - tol_y, 14.0)
    # 2. T-Track Flange Retention (Segment 2)
    with Locations((47.25, btn_y, 35.0)):
        Box(2.5 - tol_x, 9.2 - tol_y, 14.0)
    # 3. Intermediate Nib Neck (Segment 3)
    with Locations((45.35, btn_y, 35.0)):
        Box(1.3 - tol_x, 5.4 - tol_y, 14.0)
    # 4. Switch Hold-Down Block (Segment 4, sits 0.4mm above switch top at Z=31.0)
    with Locations((42.80, btn_y, 35.0)):
        Box(3.8 - tol_x, 6.6 - tol_y, 14.0)

    # Cut concave clearance arches at bottom
    with Locations((50.25, btn_y, btn_z)):
        Cylinder(radius=3.2, height=4.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    with Locations((47.25, btn_y, btn_z)):
        Cylinder(radius=4.6, height=3.5, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    with Locations((45.35, btn_y, btn_z)):
        Cylinder(radius=2.7, height=2.5, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    # Trim bottom of switch hold-down block to Z=31.4 (0.4mm above switch top)
    with Locations((42.80, btn_y, 25.0)):
        Box(10.0, 10.0, 12.8, mode=Mode.SUBTRACT)

# Trim top face with bottom_mask_solid lowered by 0.15mm (sub-flush to 14.68° parting seam):
button_keystone = keystone_builder.part & bottom_mask_solid.moved(Location((0, 0, -0.15)))

# Bottom Tub Cradle Boss & U-Slot Cutouts
# Solid pedestal roots seamlessly all the way down into the inclined floor (Z = 13.5 to 25.0mm)
# and a rear open slit for the solder legs to exit freely into the terminal interior.
cradle_w = 14.0      # Y in [25.0, 39.0]
cradle_depth = 8.5  # X in [37.0, 45.5] (retains robust side pillars)
cradle_cx = 45.5 - cradle_depth / 2 # 41.25
cradle_bot_z = 10.0 # Deep root into underbelly, trimmed by solid_enclosure_bottom
cradle_h = btn_seam_z - cradle_bot_z

with BuildPart() as button_cradle_boss_raw:
    with Locations((cradle_cx, btn_y, cradle_bot_z + cradle_h / 2)):
        Box(cradle_depth, cradle_w, cradle_h)

button_cradle_boss = button_cradle_boss_raw.part & (outer_solid_boundary & bottom_mask_solid)

with BuildPart() as button_cradle_cutters:
    # 1. Outer cap U-slot: width 6.4mm, X in [48.5, 52.0]
    with Locations((50.25, btn_y, btn_z)):
        Cylinder(radius=6.4 / 2, height=4.0, rotation=(0, 90, 0))
    with Locations((50.25, btn_y, btn_z + (40.0 - btn_z) / 2)):
        Box(4.0, 6.4, 40.0 - btn_z)

    # 2. T-track U-slot: width 9.2mm, X in [46.0, 48.5] (depth 2.5mm for 1.0mm travel)
    with Locations((47.25, btn_y, btn_z)):
        Cylinder(radius=9.2 / 2, height=2.5, rotation=(0, 90, 0))
    with Locations((47.25, btn_y, btn_z + (40.0 - btn_z) / 2)):
        Box(2.5, 9.2, 40.0 - btn_z)

    # 3. Fat nib aperture: width 5.4mm, X in [44.7, 46.0]
    with Locations((45.35, btn_y, btn_z)):
        Cylinder(radius=5.4 / 2, height=1.3, rotation=(0, 90, 0))
    with Locations((45.35, btn_y, btn_z + (40.0 - btn_z) / 2)):
        Box(1.3, 5.4, 40.0 - btn_z)

    # 4. Switch pocket: width 6.6mm, depth 3.8mm, X in [40.9, 44.7]
    # Sits on the solid pedestal at Z = 25.0mm (zero cuts below Z = 25.0mm!)
    pocket_cx = (40.9 + 44.7) / 2
    pocket_depth = 44.7 - 40.9
    with Locations((pocket_cx, btn_y, 25.0 + (40.0 - 25.0) / 2)):
        Box(pocket_depth, 6.6, 40.0 - 25.0)

    # 5. Rear Leg Slit: single narrow vertical line (1.6mm wide) for vertically aligned button legs!
    # Cuts through the back wall into the case interior: X in [36.0, 41.5], Z in [24.5, 40.0]
    slit_cx = (36.0 + 41.5) / 2
    slit_depth = 41.5 - 36.0
    with Locations((slit_cx, btn_y, 24.5 + (40.0 - 24.5) / 2)):
        Box(slit_depth, 1.6, 40.0 - 24.5)

case_bottom = (case_bottom + button_cradle_boss) - button_cradle_cutters.part

print("Case Top Volume:", case_top.volume)
print("Case Bottom Volume:", case_bottom.volume)
print("Button Plunger Volume:", button_plunger.volume)
print("Button Keystone Volume:", button_keystone.volume)

if __name__ == "__main__":
    # ==========================================
    # 6. EXPORT STEP & STL
    # ==========================================
    export_step(case_top, "case_top_b123d.step")
    export_step(case_bottom, "case_bottom_b123d.step")
    export_step(button_plunger, "test_button_plunger.step")
    export_step(button_keystone, "test_button_keystone.step")
    export_stl(case_top, "case_top_b123d.stl", tolerance=0.02, angular_tolerance=0.1)
    export_stl(case_bottom, "case_bottom_b123d.stl", tolerance=0.02, angular_tolerance=0.1)
    export_stl(button_plunger, "test_button_plunger.stl", tolerance=0.02, angular_tolerance=0.1)
    export_stl(button_keystone, "test_button_keystone.stl", tolerance=0.02, angular_tolerance=0.1)
    print("Exported case_top, case_bottom, button_plunger, and button_keystone successfully to STEP and STL!")

    # ==========================================
    # 7. STREAM TO OCP CAD VIEWER IN VS CODE
    # ==========================================
    try:
        from ocp_vscode import show, reset_show, set_port
        set_port(3939)
        reset_show()
        # Display both halves in the viewer
        show(
            case_top.moved(Location((-75, 0, 0))),
            case_bottom.moved(Location((75, 0, 0))),
            names=["case_top_lid", "case_bottom_tub"],
            colors=["#708090", "#2F4F4F"]
        )
        print("Sent both case halves to OCP CAD Viewer!")
    except Exception as e:
        print("OCP Viewer notice:", e)
