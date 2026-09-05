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
wall = 3.5
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
lip_t = 1.5
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
        offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-wall)
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
        with Locations((-screen_ribbon_gap / 2, 0)):
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
        with Locations((-screen_ribbon_gap / 2, 0)):
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
    with BuildSketch(Plane.YZ):
        offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-lip_t)
    outer_lip_ext = extrude(amount=(enc_width - 2 * lip_t) / 2, both=True, mode=Mode.PRIVATE)
    
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
                    Rectangle(15, 10.1)
            extrude(amount=-100)
        with BuildSketch(Plane.XY.offset(50)):
            with Locations((0, 170)):
                Rectangle(enc_width + 10, 50)
        extrude(amount=-100)
        
    lip_positive = lip_positive - masks.part

lip_positive_solid = lip_positive

with BuildPart() as neg_lip:
    with BuildSketch(Plane.YZ):
        offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-lip_t + lip_tol)
    outer_neg_ext = extrude(amount=(enc_width - 2 * lip_t + 2 * lip_tol) / 2, both=True, mode=Mode.PRIVATE)
    
    with BuildSketch(Plane.YZ):
        offset(Polygon([p1, p2, p3, p5, p6, p7]), amount=-wall - lip_tol)
    inner_neg_ext = extrude(amount=(enc_width - 2 * wall - 2) / 2, both=True, mode=Mode.PRIVATE)
    
    neg_ribbon = outer_neg_ext - inner_neg_ext
    lip_negative = neg_ribbon & (bottom_mask_solid.moved(Location((0, 0, lip_h + 0.3))))
    
    with BuildPart() as masks:
        for bx, by in boss_locs:
            with BuildSketch(Plane.XY.offset(50)):
                with Locations((bx, by)):
                    Rectangle(15, 10.1)
            extrude(amount=-100)
        with BuildSketch(Plane.XY.offset(50)):
            with Locations((0, 170)):
                Rectangle(enc_width + 10, 50)
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

# Blind Heat-Set Insert Holes in Top Lid (M3 x 4mm insert: hole diameter 4.0mm, depth 6.5mm)
with BuildPart() as insert_holes:
    for bx, by in boss_locs:
        z_cut = get_seam_z(by)
        # Blind cylindrical hole drilled UPWARDS from the parting seam into the boss
        with BuildSketch(Plane.XY.offset(z_cut - 0.1)):
            with Locations((bx, by)):
                Circle(radius=4.0 / 2)
        extrude(amount=6.6)
        # 45 deg lead-in chamfer for easy alignment when pressing with soldering iron
        with BuildSketch(Plane.XY.offset(z_cut - 0.1)):
            with Locations((bx, by)):
                Circle(radius=4.6 / 2)
        extrude(amount=0.8)
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
        # Front: 3.5mm deep (flange = 6.5mm, uses M3x12mm screw)
        # Back: 48.0mm deep (flange = 14.4mm, uses M3x18mm or M3x20mm screw)
        cb_depth = 48.0 if by > 50 else 3.5
        with BuildSketch(Plane.XY.offset(-1)):
            with Locations((bx, by)):
                Circle(radius=6.5 / 2)
        extrude(amount=cb_depth + 1)
case_bottom = case_bottom - bottom_screw_holes.part

print("Case Top Volume:", case_top.volume)
print("Case Bottom Volume:", case_bottom.volume)

# ==========================================
# 6. EXPORT STEP & STL
# ==========================================
export_step(case_top, "case_top_b123d.step")
export_step(case_bottom, "case_bottom_b123d.step")
export_stl(case_top, "case_top_b123d.stl", tolerance=0.02, angular_tolerance=0.1)
export_stl(case_bottom, "case_bottom_b123d.stl", tolerance=0.02, angular_tolerance=0.1)
print("Exported case_top and case_bottom successfully to STEP and STL!")

# ==========================================
# 7. STREAM TO OCP CAD VIEWER IN VS CODE
# ==========================================
try:
    from ocp_vscode import show, reset_show
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
