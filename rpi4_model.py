"""
rpi4_model.py
-------------
Imports and aligns the official Raspberry Pi 4 Model B STEP model
onto the DFR0550-V2 screen standoffs inside the 3D POS Terminal enclosure.

Mating Coordinate Alignment:
- Centers the 4 mounting holes (58.0 mm x 49.0 mm) at (0, 0).
- Bottom face of the PCB sits flush on the standoff tips at Z = 0.
- Components (CPU, heatsinks, USB, Ethernet, GPIO) extend inward into the casing.
"""

from build123d import *
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
import os

# Path to official STEP model
STEP_PATH = os.path.join(
    os.path.dirname(__file__),
    "extra_cad_files/raspberry-pi-4-model-b-1.snapshot.3/Raspberry Pi 4 Model B.STEP"
)

# Standard Raspberry Pi 4 B Mounting Dimensions
RPI_HOLE_SPAN_X = 58.0   # Along length
RPI_HOLE_SPAN_Y = 49.0   # Along width
RPI_PCB_T = 1.58         # PCB thickness (mm)


def load_raw_rpi4() -> Compound:
    """Loads the raw STEP model from disk."""
    if not os.path.exists(STEP_PATH):
        raise FileNotFoundError(f"RPi 4 STEP file not found at: {STEP_PATH}")
    return import_step(STEP_PATH)


def get_rpi4_centered(raw_rpi: Compound = None) -> Compound:
    """
    Returns the RPi 4 model with the 4 mounting holes centered at (0, 0)
    and the PCB bottom face resting at Y = 0 (components extending in +Y).
    """
    if raw_rpi is None:
        raw_rpi = load_raw_rpi4()

    # Hole centers in raw STEP: X = -10.0, Z = 0.0, PCB bottom at Y = -0.79
    # Shift X by +10.0, Y by +0.79 to normalize
    shift = Location((10.0, 0.79, 0.0))
    trsf = shift.wrapped.Transformation()
    transformer = BRepBuilderAPI_Transform(raw_rpi.wrapped, trsf, True)
    return Compound(transformer.Shape())


def get_rpi4_assembly(screen_plane: Plane, orientation: str = "peak", raw_rpi: Compound = None, use_cache: bool = True) -> Compound:
    """
    Mates the Raspberry Pi 4 onto the 4 brass standoffs on the back of the DFR0550-V2 screen.
    Uses native BREP cache when available for near-instant (<0.5s) loading.
    """
    cache_path = os.path.join(os.path.dirname(__file__), "rpi4_placed.brep")
    if orientation == "peak" and use_cache and os.path.exists(cache_path):
        from OCP.BRepTools import BRepTools
        from OCP.BRep import BRep_Builder
        from OCP.TopoDS import TopoDS_Shape
        builder = BRep_Builder()
        shape = TopoDS_Shape()
        if BRepTools.Read_s(shape, cache_path, builder):
            return Compound(shape)

    centered = get_rpi4_centered(raw_rpi)

    # Standoff offset is -1.82mm when screen is rotated 180 (peak), and +1.82mm in chin mode
    standoff_y_offset = -1.82 if orientation == "peak" else 1.82
    standoff_origin = screen_plane.from_local_coords((0, standoff_y_offset, -12.4))
    ydir = screen_plane.y_dir
    xdir = screen_plane.x_dir

    if orientation == "chin":
        # USB/Ethernet (+X_rpi) -> -Y_plane (chin)
        # Type-C/HDMI (+Z_rpi)   -> +X_plane (right wall)
        # Components (+Y_rpi)    -> -Z_plane (inward into tub)
        target_plane = Plane(origin=standoff_origin, x_dir=-ydir, z_dir=xdir)
    elif orientation == "peak":
        # USB/Ethernet (+X_rpi) -> +Y_plane (peak)
        # Type-C/HDMI (+Z_rpi)   -> -X_plane (left wall)
        # Components (+Y_rpi)    -> -Z_plane (inward into tub)
        target_plane = Plane(origin=standoff_origin, x_dir=ydir, z_dir=-xdir)
    else:
        raise ValueError(f"Unknown orientation: {orientation}. Choose 'chin' or 'peak'.")

    # Transform geometry cleanly into target plane
    trsf = target_plane.location.wrapped.Transformation()
    transformer = BRepBuilderAPI_Transform(centered.wrapped, trsf, True)
    return Compound(transformer.Shape())


if __name__ == "__main__":
    import math
    print("Testing RPi 4 Model loading and alignment...")
    # Test screen plane matching enclosure_b123d.py
    face_angle = math.atan2(55.0, 210.0)
    test_screen_plane = Plane(
        origin=(0, 60.0, 68.0476),
        x_dir=(1, 0, 0),
        z_dir=(0, -math.sin(face_angle), math.cos(face_angle))
    )
    
    rpi_chin = get_rpi4_assembly(test_screen_plane, orientation="chin")
    bb = rpi_chin.bounding_box()
    print("RPi 4 Chin orientation aligned successfully!")
    print(f"World Bounding Box: X=[{bb.min.X:.2f}, {bb.max.X:.2f}], Y=[{bb.min.Y:.2f}, {bb.max.Y:.2f}], Z=[{bb.min.Z:.2f}, {bb.max.Z:.2f}]")
