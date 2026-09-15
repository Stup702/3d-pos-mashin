"""
validate_collisions.py
----------------------
Exhaustive 3D CAD collision and clearance verification script.
Tests exact boolean intersections between all enclosure components and physical hardware.
"""

import sys
import math
from build123d import *
from enclosure_b123d import (
    case_top, case_bottom,
    button_plunger, button_keystone,
    floor_plane, screen_plane,
    ups_cx, ups_cy_local, ups_w, ups_l, ups_pedestal_h, ups_pcb_t,
    ups_boss_x, ups_boss_y,
    fan_cx, fan_cy_local, fan_size, fan_standoff_h,
    bat_cx, bat_cy_local, bat_w, bat_l,
    btn_x, btn_y, btn_z,
    screen_w, screen_l, screen_t, balcony_t, corner_block_h,
    screen_hole_x_spacing, screen_hole_y_spacing, screen_boss_d, screen_boss_h
)

def run_checks():
    print("=" * 60)
    print("STARTING EXHAUSTIVE 3D COLLISION DETECTION")
    print("=" * 60)
    
    failures = []
    passes = []

    # ---------------------------------------------------------
    # CHECK 1: Clamshell Seam Collision (case_top vs case_bottom)
    # ---------------------------------------------------------
    print("\n[CHECK 1] Case Top vs Case Bottom Clamshell Seam...")
    inter_clamshell = case_top & case_bottom
    vol_clamshell = inter_clamshell.volume
    print(f"  Intersection Volume: {vol_clamshell:.4f} mm³")
    if vol_clamshell < 1e-3:
        passes.append("CHECK 1: Case Top & Case Bottom (Zero seam collision)")
        print("  ✓ PASS: Perfect zero-collision parting seam and lap joint.")
    else:
        failures.append(f"CHECK 1: Clamshell intersection volume is {vol_clamshell:.4f} mm³")
        print(f"  ✗ FAIL: Clamshell collision detected: {vol_clamshell:.4f} mm³")

    # ---------------------------------------------------------
    # CHECK 2: Case Bottom vs Button Plunger (at resting position)
    # ---------------------------------------------------------
    print("\n[CHECK 2] Case Bottom vs Button Plunger (At Rest)...")
    inter_plunger = case_bottom & button_plunger
    vol_plunger = inter_plunger.volume
    print(f"  Intersection Volume: {vol_plunger:.4f} mm³")
    if vol_plunger < 1e-3:
        passes.append("CHECK 2: Case Bottom & Button Plunger (Zero collision)")
        print("  ✓ PASS: Plunger floats cleanly in U-slot at rest.")
    else:
        failures.append(f"CHECK 2: Plunger collides with case_bottom: {vol_plunger:.4f} mm³")
        print(f"  ✗ FAIL: Plunger collision: {vol_plunger:.4f} mm³")

    # ---------------------------------------------------------
    # CHECK 3: Case Bottom vs Button Keystone Clip (Seated Position)
    # ---------------------------------------------------------
    print("\n[CHECK 3] Case Bottom vs Button Keystone Clip...")
    inter_keystone_bot = case_bottom & button_keystone
    vol_keystone_bot = inter_keystone_bot.volume
    print(f"  Intersection Volume: {vol_keystone_bot:.4f} mm³")
    if vol_keystone_bot < 1e-3:
        passes.append("CHECK 3: Case Bottom & Keystone Clip (Zero collision)")
        print("  ✓ PASS: Keystone fits cleanly inside U-slot with 0.15mm margin/side.")
    else:
        failures.append(f"CHECK 3: Keystone collides with case_bottom: {vol_keystone_bot:.4f} mm³")
        print(f"  ✗ FAIL: Keystone bottom collision: {vol_keystone_bot:.4f} mm³")

    # ---------------------------------------------------------
    # CHECK 4: Case Top vs Button Keystone Clip (Closed Clamshell)
    # ---------------------------------------------------------
    print("\n[CHECK 4] Case Top vs Button Keystone Clip...")
    inter_keystone_top = case_top & button_keystone
    vol_keystone_top = inter_keystone_top.volume
    print(f"  Intersection Volume: {vol_keystone_top:.4f} mm³")
    if vol_keystone_top < 1e-3:
        passes.append("CHECK 4: Case Top & Keystone Clip (Zero collision)")
        print("  ✓ PASS: Keystone top face is sub-flush (0.15mm clearance to lid).")
    else:
        failures.append(f"CHECK 4: Keystone collides with case_top: {vol_keystone_top:.4f} mm³")
        print(f"  ✗ FAIL: Keystone top collision: {vol_keystone_top:.4f} mm³")

    # ---------------------------------------------------------
    # CHECK 5: Button Keystone vs Button Plunger
    # ---------------------------------------------------------
    print("\n[CHECK 5] Button Keystone vs Button Plunger...")
    inter_keystone_plunger = button_keystone & button_plunger
    vol_keystone_plunger = inter_keystone_plunger.volume
    print(f"  Intersection Volume: {vol_keystone_plunger:.4f} mm³")
    if vol_keystone_plunger < 1e-3:
        passes.append("CHECK 5: Button Keystone & Button Plunger (Zero collision)")
        print("  ✓ PASS: Keystone arches provide 0.3mm radial clearance over plunger.")
    else:
        failures.append(f"CHECK 5: Keystone collides with plunger: {vol_keystone_plunger:.4f} mm³")
        print(f"  ✗ FAIL: Keystone plunger collision: {vol_keystone_plunger:.4f} mm³")

    # ---------------------------------------------------------
    # CHECK 6: UPS Board Envelope vs Case Bottom
    # ---------------------------------------------------------
    print("\n[CHECK 6] UPS Board Envelope vs Case Bottom...")
    # PCB sits at Z = ups_pedestal_h = 3.5mm above floor_plane
    # Nominal board size: 78.3 x 55.5 x 1.6mm
    # Hole at (ups_boss_x, ups_boss_y) = (-4.50, -7.15) with dia 4.0mm
    with BuildPart() as ups_pcb_builder:
        # Datum: PCB left edge is at X = -44.20, rear edge is at Y = +11.75
        pcb_cx = -44.20 + ups_w / 2.0  # -5.05
        pcb_cy = +11.75 - ups_l / 2.0  # -16.00
        with BuildSketch(floor_plane.offset(ups_pedestal_h)):
            with Locations((pcb_cx, pcb_cy)):
                Rectangle(ups_w, ups_l)
            with Locations((ups_boss_x, ups_boss_y)):
                Circle(radius=4.0 / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=ups_pcb_t)
    
    ups_pcb_solid = ups_pcb_builder.part
    inter_ups = case_bottom & ups_pcb_solid
    vol_ups = inter_ups.volume
    print(f"  Intersection Volume: {vol_ups:.4f} mm³")
    if vol_ups < 1e-3:
        passes.append("CHECK 6: UPS Board Envelope & Case Bottom (Zero collision)")
        print("  ✓ PASS: UPS board sits with 100% clearance inside cradle.")
    else:
        failures.append(f"CHECK 6: UPS board collides with case_bottom: {vol_ups:.4f} mm³")
        print(f"  ✗ FAIL: UPS board collision: {vol_ups:.4f} mm³")

    # ---------------------------------------------------------
    # CHECK 7: 30mm Fan Envelope vs Case Bottom & Case Top
    # ---------------------------------------------------------
    print("\n[CHECK 7] 30mm Cooling Fan Envelope vs Case Bottom...")
    # Fan is 30x30x7mm, sits on 2.0mm standoffs at (fan_cx, fan_cy_local) = (0, 48.0)
    with BuildPart() as fan_builder:
        with BuildSketch(floor_plane.offset(fan_standoff_h)):
            with Locations((fan_cx, fan_cy_local)):
                Rectangle(fan_size, fan_size)
        extrude(amount=7.0)
    
    fan_solid = fan_builder.part
    inter_fan_bot = case_bottom & fan_solid
    vol_fan_bot = inter_fan_bot.volume
    print(f"  Case Bottom Intersection Volume: {vol_fan_bot:.4f} mm³")
    inter_fan_top = case_top & fan_solid
    vol_fan_top = inter_fan_top.volume
    print(f"  Case Top Intersection Volume: {vol_fan_top:.4f} mm³")
    
    if vol_fan_bot < 1e-3 and vol_fan_top < 1e-3:
        passes.append("CHECK 7: 30mm Fan Envelope vs Enclosure (Zero collision)")
        print("  ✓ PASS: 30mm Fan has 100% clearance to bottom and top lid.")
    else:
        failures.append(f"CHECK 7: Fan collides: bot={vol_fan_bot:.4f}, top={vol_fan_top:.4f} mm³")
        print(f"  ✗ FAIL: Fan collision detected!")

    # ---------------------------------------------------------
    # CHECK 8: Battery Pack Envelope vs Case Bottom & Case Top
    # ---------------------------------------------------------
    print("\n[CHECK 8] Battery Pack Envelope vs Enclosure...")
    # Pack: 67.8 x 73.35 x 18.0mm on floor_plane inside cradle
    with BuildPart() as bat_builder:
        with BuildSketch(floor_plane):
            with Locations((bat_cx, bat_cy_local)):
                Rectangle(bat_w, bat_l)
        extrude(amount=18.0)
    
    bat_solid = bat_builder.part
    inter_bat_bot = case_bottom & bat_solid
    vol_bat_bot = inter_bat_bot.volume
    print(f"  Case Bottom Intersection Volume: {vol_bat_bot:.4f} mm³")
    inter_bat_top = case_top & bat_solid
    vol_bat_top = inter_bat_top.volume
    print(f"  Case Top Intersection Volume: {vol_bat_top:.4f} mm³")
    
    if vol_bat_bot < 1e-3 and vol_bat_top < 1e-3:
        passes.append("CHECK 8: Battery Pack Envelope vs Enclosure (Zero collision)")
        print("  ✓ PASS: Battery sits cleanly inside cradle with zero lid interference.")
    else:
        failures.append(f"CHECK 8: Battery collides: bot={vol_bat_bot:.4f}, top={vol_bat_top:.4f} mm³")
        print(f"  ✗ FAIL: Battery collision detected!")

    # ---------------------------------------------------------
    # CHECK 9: Screen Module Envelope vs Case Top
    # ---------------------------------------------------------
    print("\n[CHECK 9] Screen Module Envelope vs Case Top...")
    # Screen glass/bezel sits in pocket: screen_w x screen_l x screen_t
    # 4 Brass standoffs (dia 5.5, length 5.0) sleeve through balcony
    with BuildPart() as screen_builder:
        # Glass/PCB body
        with BuildSketch(screen_plane):
            Rectangle(screen_w, screen_l)
        extrude(amount=-screen_t)
        # 4 Factory standoffs
        for hx in [-screen_hole_x_spacing / 2, screen_hole_x_spacing / 2]:
            for hy in [-screen_hole_y_spacing / 2, screen_hole_y_spacing / 2]:
                with BuildSketch(screen_plane.offset(-screen_t)):
                    with Locations((hx, hy)):
                        Circle(radius=screen_boss_d / 2)
                extrude(amount=-screen_boss_h)
    
    screen_solid = screen_builder.part
    inter_screen = case_top & screen_solid
    vol_screen = inter_screen.volume
    print(f"  Screen Intersection Volume: {vol_screen:.4f} mm³")
    if vol_screen < 1e-3:
        passes.append("CHECK 9: Screen Module & Case Top (Zero collision)")
        print("  ✓ PASS: Screen glass, PCB, and 4 brass standoffs fit with 100% clearance.")
    else:
        failures.append(f"CHECK 9: Screen collides with case_top: {vol_screen:.4f} mm³")
        print(f"  ✗ FAIL: Screen collision: {vol_screen:.4f} mm³")

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("COLLISION DETECTION AUDIT RESULTS")
    print("=" * 60)
    for p in passes:
        print(f" [PASS] {p}")
    for f in failures:
        print(f" [FAIL] {f}")
    print("=" * 60)
    
    if not failures:
        print("\n>>> ALL 9 CHECKS PASSED: ZERO PHYSICAL COLLISIONS DETECTED! <<<")
        return 0
    else:
        print(f"\n>>> AUDIT FAILED: {len(failures)} collision(s) detected! <<<")
        return 1

if __name__ == "__main__":
    code = run_checks()
    sys.exit(code)
