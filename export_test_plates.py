"""
export_test_plates.py
---------------------
Generates small, fast test-print gauge plates for rapid physical validation:
1. test_plate_battery.stl  - Battery cradle friction-fit check (~20 min print)
2. test_plate_ups.stl      - UPS cradle, 3.5mm boss, corner pads, & DC jack check (~25 min print)
3. test_plate_screen.stl   - Screen flush fit, balcony, standoffs, & DSI slot check (~40 min print)
"""

from build123d import *
import os

OUTPUT_DIR = os.path.dirname(__file__)

# ==========================================
# 1. BATTERY TEST PLATE
# ==========================================
def make_battery_test_plate(bat_h: float = 10.0) -> Compound:
    bat_w = 67.80
    bat_l = 73.35
    bat_tol = 0.6
    bat_wall = 1.5
    base_t = 2.0

    with BuildPart() as bp:
        # 1. Flat base plate Z in [-base_t, 0]
        with BuildSketch(Plane.XY.offset(-base_t)):
            Rectangle(bat_w + bat_tol + 2 * bat_wall + 8.0, bat_l + bat_tol + 2 * bat_wall + 8.0)
        extrude(amount=base_t)

        # 2. 10mm Cradle retention walls Z in [0, bat_h]
        with BuildSketch(Plane.XY):
            Rectangle(bat_w + bat_tol + 2 * bat_wall, bat_l + bat_tol + 2 * bat_wall)
            Rectangle(bat_w + bat_tol, bat_l + bat_tol, mode=Mode.SUBTRACT)
        extrude(amount=bat_h)

    return bp.part

# ==========================================
# 2. UPS TEST PLATE
# ==========================================
def make_ups_test_plate() -> Compound:
    ups_w = 79.15
    ups_l = 54.50
    ups_tol = 0.6
    ups_wall = 1.5
    ups_pedestal_h = 3.5
    ups_pcb_t = 1.6
    ups_total_h = ups_pedestal_h + ups_pcb_t # 5.1mm
    base_t = 2.0

    # Boss coordinates relative to PCB center
    boss_x = -ups_w / 2.0 + 39.70 # -4.00 mm from left wall relative to center
    boss_y = ups_l / 2.0 - 18.90   # -7.65 mm from fan edge relative to center

    with BuildPart() as bp:
        # 1. Flat base plate Z in [-base_t, 0]
        with BuildSketch(Plane.XY.offset(-base_t)):
            Rectangle(ups_w + ups_tol + 2 * ups_wall + 8.0, ups_l + ups_tol + 2 * ups_wall + 8.0)
        extrude(amount=base_t)

        # 2. 3.5mm Standoff Boss with 4.0mm hole (Z in [0, 3.5])
        with BuildSketch(Plane.XY):
            with Locations((boss_x, boss_y)):
                Circle(radius=8.0 / 2)
                Circle(radius=4.0 / 2, mode=Mode.SUBTRACT)
        extrude(amount=ups_pedestal_h)

        # 3. 4 Corner Support Pads (3.5mm tall) (Z in [0, 3.5])
        pad_size = 5.0
        with BuildSketch(Plane.XY):
            for px in [-(ups_w + ups_tol) / 2 + pad_size / 2, (ups_w + ups_tol) / 2 - pad_size / 2]:
                for py in [-(ups_l + ups_tol) / 2 + pad_size / 2, (ups_l + ups_tol) / 2 - pad_size / 2]:
                    with Locations((px, py)):
                        Rectangle(pad_size, pad_size)
        extrude(amount=ups_pedestal_h)

        # 4. 5.1mm Friction-Fit Perimeter Wall (Z in [0, 5.1])
        with BuildSketch(Plane.XY):
            Rectangle(ups_w + ups_tol + 2 * ups_wall, ups_l + ups_tol + 2 * ups_wall)
            Rectangle(ups_w + ups_tol, ups_l + ups_tol, mode=Mode.SUBTRACT)
        extrude(amount=ups_total_h)

        # 5. Left Reference Wall with 11mm DC Barrel Jack Hole (Z in [0, 16.0])
        wall_x = -(ups_w + ups_tol + 2 * ups_wall + 8.0) / 2 + 1.5
        jack_y = -(ups_l / 2) + 14.0
        jack_z = ups_pedestal_h + 5.5 # 9.0mm above floor
        with Locations((wall_x, 0, 16.0 / 2)):
            Box(3.0, ups_l + ups_tol + 2 * ups_wall + 8.0, 16.0)
        with Locations((wall_x, jack_y, jack_z)):
            Cylinder(radius=11.0 / 2, height=10.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    return bp.part

# ==========================================
# 3. SCREEN TEST PLATE
# ==========================================
def make_screen_test_plate(dsi_gap_w: float = 22.0, dsi_gap_x: float = 0.0) -> Compound:
    screen_w = 75.8
    screen_l = 120.8
    screen_ribbon_gap = 1.5
    pocket_w = screen_w + screen_ribbon_gap + 0.4 # 77.7 mm
    pocket_l = screen_l + 0.4                     # 121.2 mm
    pocket_depth = 5.0                             # 5.0mm depth for glass + bezel
    standoff_depth = 5.2                           # Full 5.2mm sleeve for 5.0mm brass standoff
    base_pad_h = 2.0                               # 2.0mm backing shoulder for M2.5 screw
    hole_x = 68.0
    hole_y = 113.0

    frame_w = pocket_w + 6.0  # 83.7 mm
    frame_l = pocket_l + 6.0  # 127.2 mm
    shelf_z = base_pad_h + standoff_depth # 7.2 mm
    total_h = shelf_z + pocket_depth      # 12.2 mm

    with BuildPart() as bp:
        # 1. Main outer solid block with central open viewing window (Z in [0, total_h])
        with BuildSketch(Plane.XY):
            Rectangle(frame_w, frame_l)
            # Central viewing window is a COMPLETE through-hole:
            Rectangle(screen_w - 18.0, screen_l - 18.0, mode=Mode.SUBTRACT)
        extrude(amount=total_h)

        # 2. Screen Pocket (recess from Z = shelf_z to Z = total_h)
        with BuildSketch(Plane.XY.offset(shelf_z)):
            with Locations((screen_ribbon_gap / 2, 0)):
                Rectangle(pocket_w, pocket_l)
            Rectangle(screen_w - 18.0, screen_l - 18.0, mode=Mode.SUBTRACT)
        extrude(amount=pocket_depth + 1.0, mode=Mode.SUBTRACT)

        # 3. 5.2mm Deep Standoff Sleeves (dia 6.0mm) from Z = shelf_z down to Z = base_pad_h
        with BuildSketch(Plane.XY.offset(shelf_z)):
            for sx in [-hole_x / 2, hole_x / 2]:
                for sy in [-hole_y / 2, hole_y / 2]:
                    with Locations((sx, sy)):
                        Circle(radius=6.0 / 2) # dia 6.0mm for 5.0mm brass standoff
        extrude(amount=-standoff_depth, mode=Mode.SUBTRACT)

        # 4. M2.5 Screw Clearance Holes (dia 3.0mm) through the 2.0mm base pad
        with BuildSketch(Plane.XY):
            for sx in [-hole_x / 2, hole_x / 2]:
                for sy in [-hole_y / 2, hole_y / 2]:
                    with Locations((sx, sy)):
                        Circle(radius=3.0 / 2)
        extrude(amount=base_pad_h + 0.1, mode=Mode.SUBTRACT)

        # 5. DSI Cable Pass-Through Notch on Front Chin (-Y)
        with BuildSketch(Plane.XY):
            with Locations((dsi_gap_x, -frame_l / 4)):
                Rectangle(dsi_gap_w, frame_l / 2)
        extrude(amount=shelf_z + 0.1, mode=Mode.SUBTRACT)

    return bp.part


if __name__ == "__main__":
    print("Generating rapid test-print gauge plates...")
    
    bat_plate = make_battery_test_plate(bat_h=10.0)
    ups_plate = make_ups_test_plate()
    scr_plate = make_screen_test_plate(dsi_gap_w=22.0, dsi_gap_x=0.0)

    export_stl(bat_plate, os.path.join(OUTPUT_DIR, "test_plate_battery.stl"), tolerance=0.05, angular_tolerance=0.2)
    export_stl(ups_plate, os.path.join(OUTPUT_DIR, "test_plate_ups.stl"), tolerance=0.05, angular_tolerance=0.2)
    export_stl(scr_plate, os.path.join(OUTPUT_DIR, "test_plate_screen.stl"), tolerance=0.05, angular_tolerance=0.2)

    print("✓ Successfully exported:")
    print("  1. test_plate_battery.stl")
    print("  2. test_plate_ups.stl")
    print("  3. test_plate_screen.stl")
