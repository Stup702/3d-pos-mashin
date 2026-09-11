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

---

## Master Enclosure Geometry & Profile Specification

### 1. Side Profile & Inclined Underbelly (Desk Clearance)
The side profile is a wedge defined by the polygon:
* `p1 = (-70.0, 0.0)`  — Front tip (touches desk at $Z=0$)
* `p2 = (-70.0, 34.0)` — Front vertical chin
* `p3 = (140.0, 89.0)` — Top peak (sloped screen face from $p_2 \to p_3$ at $14.68^\circ$)
* `p5 = (180.0, 0.0)`  — Rear desk contact tip
* `p6 = (160.0, 0.0)`  — Rear foot baseline (touches desk at $Z=0$)
* `p7 = (140.0, 30.0)` — Slanted underbelly junction to rear foot

**CRITICAL GEOMETRIC FACT: The underbelly floor is INCLINED at $8.13^\circ$:**
* The underbelly runs from $p_1 (-70, 0)$ up to $p_7 (140, 30)$.
* Desk contact occurs **ONLY at the very front ($Y=-70$) and the rear foot ($Y=160\text{ to }180$)**.
* The entire middle floor ($Y \in [-65, 155]$) is **suspended in mid-air above the desk**!
* At the cooling fan ($Y = +48.0$), the outer underbelly skin is **$16.86\text{ mm}$ elevated above the desk**! Screw heads or intake air slots underneath the fan do **NOT** touch or drag on the desk.

### 2. Internal Components Layout (Front to Back)
1. **Screen & RPi 4**:
   * DFRobot 5" DFR0550-V2 display on top sloped face ($14.68^\circ$), flush glass drop, 5.0mm brass standoff sleeves, 22mm DSI ribbon slot.
   * RPi 4 Model B mounted on the screen back in "peak" orientation (GPIO header on right $+X$ side, USB/LAN facing rear $+Y$).
2. **UPS Module**:
   * $78.30\text{ mm} \times 55.50\text{ mm}$, centered at $(X = -5.05, Y = -16.00)$ on the slanted floor.
   * Toolless Locating Pole: $3.5\text{ mm}$ shoulder ($\varnothing 8.0\text{ mm}$) with a $4.0\text{ mm}$ tall locating pole ($\varnothing 3.70\text{ mm}$) fitting into the PCB's $4.0\text{ mm}$ hole and protruding $2.4\text{ mm}$ above the board for hot glue gun adhesion. No screws needed near delicate chips!
   * DC barrel jack: Left wall port hole ($11\text{ mm}$ split across parting line) at $Y = -10.75\text{ mm}$.
   * Cable pass-through notch: On fan-side rear wall at $X = +16.0\text{ mm}$, width $12.0\text{ mm}$, cut flush to the inner floor for female Dupont jumper wires.
3. **Cooling Fan (LD3007MS 30mm Pi-FAN)**:
   * $30\text{ mm} \times 30\text{ mm} \times 7\text{ mm}$, centered at $(X = 0, Y = +48.0\text{ mm})$.
   * Mounting pitch: $24.0\text{ mm} \times 24.0\text{ mm}$.
   * Fasteners: $2.3\text{ mm} \times 14\text{ mm}$ pan/button head screws inserted from underside into hex nuts on top of fan frame.
   * Clearance holes: $\varnothing 2.6\text{ mm}$ through $3.5\text{ mm}$ floor and $2.0\text{ mm}$ standoffs.
   * Underbelly counterbores: $\varnothing 5.2\text{ mm} \times 1.5\text{ mm}$ deep (leaves $2.0\text{ mm}$ floor flange). Total clamped stack: $2.0\text{ mm} + 2.0\text{ mm} + 7.0\text{ mm} = 11.0\text{ mm}$, leaving $3.0\text{ mm}$ thread protrusion for full hex nut engagement.
   * Air intake vents in the slanted floor directly beneath it.
   * Elevated $\approx 16.9\text{ mm}$ above the desk.
4. **Battery Pack**:
   * $67.80\text{ mm} \times 73.35\text{ mm} \times 17.00\text{ mm}$, centered at $(X = 0, Y = +104.5\text{ mm})$ before the rear drop.
   * Retention wall: $10.0\text{ mm}$ tall.
5. **PN532 NFC Module**:
   * Slider slot embedded in the rear sloped panel ($p_3 \to p_5$).
6. **Case Fasteners**:
   * 4 main M3 casing screws (M3 $\times$ 16mm) inserted from desk base underneath into internal pillars at $(\pm 42, -50)$ ($3.5\text{ mm}$ counterbore) and $(\pm 42, 130)$ ($50.5\text{ mm}$ counterbore, leaving $11.9\text{ mm}$ flange). Top lid receives M3 brass heat-set inserts.
