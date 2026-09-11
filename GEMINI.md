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
   * $78.30\text{ mm} \times 55.50\text{ mm}$ PCB. Pocket expanded with $+1.0\text{ mm}$ give on right ($+X$) and top ($+Y$) ($79.90\text{ mm} \times 57.10\text{ mm}$, centered at $X = -4.55, Y = -15.50$), eliminating perimeter friction while keeping left stop at $X = -44.50\text{ mm}$ and front stop at $Y = -44.05\text{ mm}$ fixed.
   * Toolless Locating Pole: $3.5\text{ mm}$ shoulder ($\varnothing 8.0\text{ mm}$) at fixed coordinates $(X = -4.50, Y = -7.15\text{ mm})$. Pin diameter reduced to $\varnothing 3.45\text{ mm}$ (from $3.70\text{ mm}$) with a $45^\circ \times 0.8\text{ mm}$ conical lead-in pilot chamfer for painless, smooth drop-in registration into the PCB's $4.0\text{ mm}$ hole. Protrudes $2.4\text{ mm}$ above the PCB for hot glue gun mushrooming.
   * DC barrel jack: Left wall port ($12.0\text{ mm}$ wide along Y, $16.0\text{ mm}$ tall) and matching cradle cutout modeled with a $3.5\text{ mm}$ solid half-wall threshold from $Z = 0 \to 3.5\text{ mm}$, perfectly flush with the PCB underside. Completely blocks the view underneath the PCB and provides a rigid continuous support beam preventing PCB flex when inserting power plugs.
   * Open Corner Cable Bay: Upper-right corner of the cradle wall is cut open ($X \in [3.0, 43.0]\text{ mm}$, $Y \in [-7.0, 16.0]\text{ mm}$, flush to inner floor), reducing top wall length by another $1.0\text{ cm}$ toward the left for maximum wiring clearance. Standalone top-right corner pillar removed; 3 remaining corner pads (bottom-left, bottom-right, top-left) plus central boss shoulder form an unshakeable quad-point kinematic support plane.
3. **Right-Wall Power Button System (Option A: Drop-in T-Plunger with Full Fat Nib)**:
   * Location: Right wall outer face at $X = +50.0\text{ mm}$, inner face at $X = +45.5\text{ mm}$, centered at $Y = +32.0\text{ mm}$, $Z = 28.0\text{ mm}$ (midway between floor and parting seam $Z = 36.71\text{ mm}$).
   * Drop-in T-Plunger: Monolithic stepped cylinder with cap ($\varnothing 5.8\text{ mm} \times 2.3\text{ mm}$, $0.8\text{ mm}$ proud at rest), retention flange ($\varnothing 8.6\text{ mm} \times 1.5\text{ mm}$), and Full Fat Nib ($\varnothing 4.8\text{ mm} \times 1.1\text{ mm}$ with $0.3\text{ mm} \times 45^\circ$ lead chamfer). $0.45\text{ mm}$ chord shaved off the bottom for horizontal printing directly on PEI bed with zero supports.
   * Vertical U-Slot Architecture: Stepped vertical channel in `case_bottom` right wall and internal cradle boss extends through the parting seam to $Z = 38.0\text{ mm}$ for effortless drop-in assembly. Features a **solid pedestal shelf from the inclined floor up to $Z = 25.0\text{ mm}$** ($Z \in [13.57, 25.0]\text{ mm}$, trimmed to `outer_solid_boundary & bottom_mask_solid` to eliminate any floating overhang over the $8.13^\circ$ underbelly) directly supporting the switch, and a **single narrow $1.6\text{ mm}$ vertical slit** in the back wall allowing the vertically-rotated switch legs to slide down and exit into the case interior.
   * Drop-in Keystone Retaining Clip (`test_button_keystone.stl`): Tiny stepped slide-in plug ($289.3\text{ mm}^3$, 3-minute print) that drops into the U-slot after plunger and switch are installed. Fills the $5.8\text{ mm}$ gap on the outer wall into a clean circular aperture ($R = 3.2\text{ mm}$), captures the flange ($R = 4.6\text{ mm}$), and holds the switch down at $Z = 31.4\text{ mm}$. Its top face matches the $14.68^\circ$ parting seam (recessed $0.15\text{ mm}$ sub-flush), and is clamped down permanently when `case_top` is closed with zero supports needed.
   * Motion Stroke: $0.3\text{ mm}$ pre-travel gap to switch dome, $0.4\text{ mm}$ dome snap travel ($0.7\text{ mm}$ total stroke), leaving $0.3\text{ mm}$ overtravel cushion before inner flange stop.
4. **Cooling Fan (LD3007MS 30mm Pi-FAN)**:
   * $30\text{ mm} \times 30\text{ mm} \times 7\text{ mm}$, centered at $(X = 0, Y = +48.0\text{ mm})$.
   * Mounting pitch: $24.0\text{ mm} \times 24.0\text{ mm}$.
   * Fasteners: $2.3\text{ mm} \times 14\text{ mm}$ pan/button head screws inserted from underside into hex nuts on top of fan frame.
   * Clearance holes: $\varnothing 2.6\text{ mm}$ through $3.5\text{ mm}$ floor and $2.0\text{ mm}$ standoffs.
   * Underbelly counterbores: $\varnothing 5.2\text{ mm} \times 1.5\text{ mm}$ deep (leaves $2.0\text{ mm}$ floor flange). Total clamped stack: $2.0\text{ mm} + 2.0\text{ mm} + 7.0\text{ mm} = 11.0\text{ mm}$, leaving $3.0\text{ mm}$ thread protrusion for full hex nut engagement.
   * Air intake vents in the slanted floor directly beneath it.
   * Elevated $\approx 16.9\text{ mm}$ above the desk.
5. **Battery Pack**:
   * $67.80\text{ mm} \times 73.35\text{ mm} \times 17.00\text{ mm}$, centered at $(X = 0, Y = +104.5\text{ mm})$ before the rear drop.
   * Retention wall: $10.0\text{ mm}$ tall.
6. **PN532 NFC Module**:
   * Slider slot embedded in the rear sloped panel ($p_3 \to p_5$).
7. **Case Fasteners**:
   * 4 main M3 casing screws (M3 $\times$ 16mm) inserted from desk base underneath into internal pillars at $(\pm 42, -50)$ ($3.5\text{ mm}$ counterbore) and $(\pm 42, 130)$ ($50.5\text{ mm}$ counterbore, leaving $11.9\text{ mm}$ flange). Top lid receives M3 brass heat-set inserts into 100% full round blind holes ($\varnothing 3.8\text{ mm} \times 6.6\text{ mm}$ deep with $\varnothing 4.1\text{ mm}$ lead-in chamfer, starting $3.0\text{ mm}$ below the parting seam to penetrate the $14.68^\circ$ sloped boss face without semicircular slicing).
