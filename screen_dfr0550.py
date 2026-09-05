"""
screen_dfr0550.py
-----------------
3D Solid Model of DFRobot 5" DSI Capacitive Touchscreen (SKU: DFR0550-V2).
Dimensions derived directly from the official 2D CAD blueprint (DFR0550-V2_2D_CAD.dxf).

Key Dimensions:
- Cover Glass: 120.8 mm x 75.8 mm x 1.8 mm
- Active Display Window: 108.0 mm x 64.8 mm
- LCD Module Body: 114.0 mm x 69.0 mm x 4.0 mm
- Screen PCB: 120.8 mm x 75.8 mm x 1.6 mm
- 4x Outer Mounting Holes: M2.5 (2.5 mm dia) at 113.0 mm x 68.0 mm spacing
- 4x Inner Standoffs for RPi 4: M2.5 brass standoffs, 5.5 mm dia x 5.0 mm tall,
  spaced 58.0 mm (along length) x 49.0 mm (along width), with +1.82 mm offset along length.
"""

from build123d import *

# Blueprint Dimensions
SCREEN_W = 75.8               # Glass width (mm)
SCREEN_L = 120.8              # Glass length (mm)
GLASS_T = 1.8                 # Chemically strengthened cover glass thickness (mm)
LCD_MODULE_T = 4.0            # Display panel module thickness (mm)
PCB_T = 1.6                   # PCB thickness (mm)
STANDOFF_D = 5.5              # Standoff outer diameter (mm)
STANDOFF_H = 5.0              # Factory brass standoff height (mm)
SCREW_HOLE_D = 2.5            # M2.5 hole diameter (mm)

# Hole Spacing
OUTER_HOLE_X = 68.0           # Spacing along width
OUTER_HOLE_Y = 113.0          # Spacing along length
RPI_HOLE_X = 49.0             # RPi standoff spacing along width
RPI_HOLE_Y = 58.0             # RPi standoff spacing along length
RPI_STANDOFF_OFFSET_Y = 1.82  # Longitudinal offset from screen center per DXF blueprint


def build_dfr0550_screen(plane: Plane) -> Compound:
    """
    Constructs a complete solid compound of the DFR0550-V2 screen assembly
    anchored to the specified plane.
    
    The front face of the cover glass is positioned flush at plane local Z = 0.
    The assembly extends in negative local Z (inward into the casing).
    """
    with BuildPart() as builder:
        # 1. Front Cover Glass (Dark tinted glass, flush at local Z = 0)
        with BuildSketch(plane.offset(-GLASS_T / 2)):
            Rectangle(SCREEN_W, SCREEN_L)
        extrude(amount=GLASS_T / 2, both=True)

        # 2. Internal LCD Panel Body & Bezel
        with BuildSketch(plane.offset(-GLASS_T - LCD_MODULE_T / 2)):
            Rectangle(SCREEN_W - 6.8, SCREEN_L - 6.8)
        extrude(amount=LCD_MODULE_T / 2, both=True)

        # 3. Main Screen Controller PCB
        pcb_z_mid = -GLASS_T - LCD_MODULE_T - (PCB_T / 2) # Local Z = -6.6 mm
        with BuildSketch(plane.offset(pcb_z_mid)):
            Rectangle(SCREEN_W, SCREEN_L)
            # 4 Outer M2.5 Mounting Holes
            for hx in [-OUTER_HOLE_X / 2, OUTER_HOLE_X / 2]:
                for hy in [-OUTER_HOLE_Y / 2, OUTER_HOLE_Y / 2]:
                    with Locations((hx, hy)):
                        Circle(radius=SCREW_HOLE_D / 2, mode=Mode.SUBTRACT)
        extrude(amount=PCB_T / 2, both=True)

        # 4. 4x Integrated Brass Standoffs for Raspberry Pi Mounting
        standoff_base_z = -GLASS_T - LCD_MODULE_T - PCB_T # Local Z = -7.4 mm
        for sx in [-RPI_HOLE_X / 2, RPI_HOLE_X / 2]:
            for sy in [-RPI_HOLE_Y / 2, RPI_HOLE_Y / 2]:
                with BuildSketch(plane.offset(standoff_base_z - STANDOFF_H / 2)):
                    with Locations((sx, sy + RPI_STANDOFF_OFFSET_Y)):
                        Circle(radius=STANDOFF_D / 2)
                        Circle(radius=SCREW_HOLE_D / 2, mode=Mode.SUBTRACT)
                extrude(amount=STANDOFF_H / 2, both=True)

    return builder.part


def get_rpi_standoff_mating_plane(screen_plane: Plane) -> Plane:
    """
    Returns the exact target Plane where the Raspberry Pi PCB bottom face mates
    against the tips of the 4 screen brass standoffs.
    """
    standoff_tip_z = -(GLASS_T + LCD_MODULE_T + PCB_T + STANDOFF_H) # -12.4 mm
    mating_origin = screen_plane.from_local_coords((0, RPI_STANDOFF_OFFSET_Y, standoff_tip_z))
    
    return Plane(
        origin=mating_origin,
        x_dir=screen_plane.x_dir,
        z_dir=screen_plane.z_dir
    )


if __name__ == "__main__":
    screen = build_dfr0550_screen(Plane.XY)
    bb = screen.bounding_box()
    print("Screen DFR0550-V2 built successfully!")
    print(f"Bounding Box: X=[{bb.min.X:.2f}, {bb.max.X:.2f}], Y=[{bb.min.Y:.2f}, {bb.max.Y:.2f}], Z=[{bb.min.Z:.2f}, {bb.max.Z:.2f}]")
    print(f"Total Volume: {screen.volume:.2f} mm^3")
