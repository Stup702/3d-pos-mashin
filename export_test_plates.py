"""
export_test_plates.py
---------------------
Generates small, fast test-print gauge plates by directly slicing the master
CAD parts from enclosure_b123d.py:
1. test_plate_screen.stl   - Screen flush fit, balcony, standoffs, & DSI slot check
2. test_plate_ups.stl      - UPS cradle, 3.5mm boss, corner pads, & DC jack check
3. test_plate_battery.stl  - Battery cradle & rear boss column clearance check

Single source of truth: any geometric update in enclosure_b123d.py automatically
updates these test plates with 100% fidelity.
"""

import os
from build123d import *
from enclosure_b123d import (
    case_top, case_bottom,
    screen_plane, floor_plane,
    ups_cx, ups_cy_local, ups_w, ups_l,
    bat_cx, bat_cy_local, bat_w, bat_l
)

OUTPUT_DIR = os.path.dirname(__file__)

def make_screen_test_plate() -> Compound:
    """Direct slice of case_top around the screen pocket and balcony."""
    loc_screen = screen_plane.location
    with BuildPart() as screen_cutter:
        with BuildSketch(screen_plane):
            Rectangle(90.0, 138.0)
        extrude(amount=-18.0)

    screen_cutout = (case_top & screen_cutter.part).moved(loc_screen.inverse())
    # Rotate 180 around X so outer face rests flat at Z=0 and pocket opens upwards
    screen_plate = screen_cutout.rotate(Axis.X, 180)
    bb = screen_plate.bounding_box()
    return screen_plate.moved(Location((-bb.center().X, -bb.center().Y, -bb.min.Z)))

def make_ups_test_plate() -> Compound:
    """Direct slice of case_bottom around the UPS cradle and DC barrel jack wall."""
    loc_floor = floor_plane.location
    with BuildPart() as ups_cutter:
        with BuildSketch(floor_plane.offset(-4.0)):
            with Locations((ups_cx - 1.0, ups_cy_local)):
                Rectangle(ups_w + 14.0, ups_l + 14.0)
        extrude(amount=25.0)

    ups_cutout = (case_bottom & ups_cutter.part).moved(loc_floor.inverse())
    with BuildPart() as floor_trim:
        with BuildSketch(Plane.XY.offset(-4.0)):
            with Locations((ups_cx - 1.0, ups_cy_local)):
                Rectangle(ups_w + 20.0, ups_l + 20.0)
        extrude(amount=50.0)
    ups_plate = (ups_cutout & floor_trim.part)
    bb = ups_plate.bounding_box()
    return ups_plate.moved(Location((-bb.center().X, -bb.center().Y, -bb.min.Z)))

def make_battery_test_plate() -> Compound:
    """Direct slice of case_bottom around the battery cradle and rear pillar clearance."""
    loc_floor = floor_plane.location
    with BuildPart() as bat_cutter:
        with BuildSketch(floor_plane.offset(-4.0)):
            with Locations((bat_cx, bat_cy_local)):
                Rectangle(bat_w + 14.0, bat_l + 14.0)
        extrude(amount=25.0)

    bat_cutout = (case_bottom & bat_cutter.part).moved(loc_floor.inverse())
    with BuildPart() as floor_trim:
        with BuildSketch(Plane.XY.offset(-4.0)):
            with Locations((bat_cx, bat_cy_local)):
                Rectangle(bat_w + 20.0, bat_l + 20.0)
        extrude(amount=50.0)
    bat_plate = (bat_cutout & floor_trim.part)
    bb = bat_plate.bounding_box()
    return bat_plate.moved(Location((-bb.center().X, -bb.center().Y, -bb.min.Z)))

if __name__ == "__main__":
    print("Generating rapid test-print gauge plates (Direct Enclosure Slice)...")
    scr_plate = make_screen_test_plate()
    ups_plate = make_ups_test_plate()
    bat_plate = make_battery_test_plate()

    export_stl(scr_plate, os.path.join(OUTPUT_DIR, "test_plate_screen.stl"), tolerance=0.05, angular_tolerance=0.2)
    export_stl(ups_plate, os.path.join(OUTPUT_DIR, "test_plate_ups.stl"), tolerance=0.05, angular_tolerance=0.2)
    export_stl(bat_plate, os.path.join(OUTPUT_DIR, "test_plate_battery.stl"), tolerance=0.05, angular_tolerance=0.2)

    print("✓ Successfully exported direct-cut test plates:")
    print("  1. test_plate_screen.stl")
    print("  2. test_plate_ups.stl")
    print("  3. test_plate_battery.stl")
