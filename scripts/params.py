# -*- coding: utf-8 -*-
"""Single source of truth for asset paths, scene constants and the tweakable parameter contract.

Every module (materials / meshes / level / tweak UI) imports from here so the
parameter set stays decoupled and consistent. Units: Unreal Units == cm.
"""

# ---------------------------------------------------------------------------
# Asset paths (package names, not filesystem paths)
# ---------------------------------------------------------------------------
ROOT      = "/Game/LiquidGlass"
MESH_PATH = ROOT + "/Meshes"
MAT_PATH  = ROOT + "/Materials"
MI_PATH   = ROOT + "/Materials/Instances"
MPC_PATH  = ROOT + "/Params"
MAP_PATH  = "/Game/LiquidGlass/Maps"

# Named assets
SM_TUMBLER = MESH_PATH + "/SM_Tumbler"
SM_LIQUID  = MESH_PATH + "/SM_Liquid"

M_GLASS    = MAT_PATH + "/M_Glass"
M_LIQUID   = MAT_PATH + "/M_Liquid"
M_ICE      = MAT_PATH + "/M_Ice"
M_STONE    = MAT_PATH + "/M_Stone"
M_TABLE    = MAT_PATH + "/M_Table"
M_BACKDROP = MAT_PATH + "/M_Backdrop"

MI_GLASS   = MI_PATH + "/MI_Glass"
MI_LIQUID  = MI_PATH + "/MI_Liquid"
MI_ICE     = MI_PATH + "/MI_Ice"
MI_STONE   = MI_PATH + "/MI_Stone"
MI_TABLE   = MI_PATH + "/MI_Table"
MI_BACKDROP= MI_PATH + "/MI_Backdrop"

MPC        = MPC_PATH + "/MPC_LiquidGlass"

LEVEL_NAME = "LiquidGlassDemo"
LEVEL_PATH = MAP_PATH + "/" + LEVEL_NAME

# ---------------------------------------------------------------------------
# Scene / geometry constants (cm)
# ---------------------------------------------------------------------------
TUMBLER = dict(
    height=9.0,          # total outer height
    radius_top=4.35,     # outer radius at the rim
    radius_bottom=3.9,   # outer radius at the base
    wall=0.34,           # wall thickness
    base=0.6,            # inner bottom height above z=0 (glass base slab)
    bevel=0.5,           # rounded bottom-corner radius
    segments=72,         # angular resolution
)

LIQUID = dict(
    fill=0.60,           # default fill fraction of the inner cavity (0..1) -> actor Z scale
    inset=0.02,          # tiny gap to the glass inner wall (cm) to avoid coplanar faces
)

# ---------------------------------------------------------------------------
# Tweakable parameter contract (MPC)
#   scalars : name -> (default, min, max)
#   vectors : name -> ((r,g,b), )
# These drive the material graph + are exposed by the tweak UI / remote control.
# ---------------------------------------------------------------------------
SCALARS = {
    "GlassIOR":          (1.50, 1.00, 2.00),
    "GlassRoughness":    (0.02, 0.00, 0.50),
    "LiquidIOR":         (1.33, 1.00, 2.00),
    "LiquidRoughness":   (0.04, 0.00, 0.50),
    "LiquidAbsorption":  (0.30, 0.00, 3.00),   # Beer-Lambert density scale
    "LiquidScattering":  (0.02, 0.00, 1.00),   # volumetric scattering scale
    "IceIOR":            (1.31, 1.00, 2.00),
    "IceRoughness":      (0.06, 0.00, 0.50),
    "KeyLightIntensity": (1.00, 0.00, 4.00),
    "RimLightIntensity": (1.00, 0.00, 4.00),
    "ExposureBias":      (0.00, -2.00, 2.00),
}

VECTORS = {
    "LiquidColor":    ((0.52, 0.30, 0.11), "amber/whisky"),
    "GlassTint":      ((1.00, 1.00, 1.00), "neutral"),
    "IceColor":       ((0.88, 0.94, 1.00), "clear ice"),
    "TableColor":     ((0.17, 0.15, 0.13), "dark wood"),
    "BackdropColor":  ((0.52, 0.56, 0.62), "neutral grey"),
}

# Default values as flat dicts for quick access
SCALAR_DEFAULTS = {k: v[0] for k, v in SCALARS.items()}
VECTOR_DEFAULTS = {k: v[0] for k, v in VECTORS.items()}
