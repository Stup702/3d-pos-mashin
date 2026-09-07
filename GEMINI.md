# 3D CAD & Modeling Guidelines

## Mandatory Roundtable Verification
Whenever creating or modifying 3D CAD models, OpenSCAD code, or 3D printable designs:
1. **Pre-flight Check**: If currently in Pro mode, ask the user to switch to **Gemini 3.7 Flash (High)**.
2. **Subagents Model**: When launching subagents, always use `Model: 'inherit'` to preserve the high reasoning mode.
3. **Roundtable Panel**: Run every geometric modification through three specialized verification roles before writing code:
   - **Trig Handler**: Calculates and double-checks exact 2D/3D coordinate geometry, angles, tangent offsets, and draft angles.
   - **3D Collision & CSG Handler**: Verifies boolean subtractions, wall thickness leeway, clearance envelopes, non-manifold prevention, and zero-thickness feather edge prevention.
   - **3D Print Expert**: Checks print bed orientation (ensuring $Z=0$ flat face adhesion without hanging overhangs), FDM shrinkage tolerances, layer overhang angles, and structural integrity.
4. **Compile Test**: Always verify the result compiles cleanly to a manifold 3D object using `openscad -o /tmp/test.stl`.
