# -*- coding: utf-8 -*-
"""Single source of truth for asset paths, scene constants and the tweakable parameter contract.

Every module imports from here. Units: Unreal Units == cm. Z is up.
"""

ROOT      = "/Game/LiquidGlass"
MESH_PATH = ROOT + "/Meshes"
MAT_PATH  = ROOT + "/Materials"
MI_PATH   = ROOT + "/Materials/Instances"
MPC_PATH  = ROOT + "/Params"
MAP_PATH  = ROOT + "/Maps"

SM_TUMBLER = MESH_PATH + "/SM_Tumbler"
SM_LIQUID  = MESH_PATH + "/SM_Liquid"

M_GLASS    = MAT_PATH + "/M_Glass"
M_LIQUID   = MAT_PATH + "/M_Liquid"
M_ICE      = MAT_PATH + "/M_Ice"
M_STONE    = MAT_PATH + "/M_Stone"
M_TABLE    = MAT_PATH + "/M_Table"
M_BACKDROP = MAT_PATH + "/M_Backdrop"

MPC        = MPC_PATH + "/MPC_LiquidGlass"
LEVEL_PATH = MAP_PATH + "/LiquidGlassDemo"

# ---------------------------------------------------------------------------
# Geometry constants (cm)
# ---------------------------------------------------------------------------
TUMBLER = dict(
    height=9.0,          # total outer height
    radius_top=4.35,     # outer radius at the rim
    radius_bottom=3.9,   # outer radius at the base
    wall=0.34,           # wall thickness
    base=0.6,            # inner bottom height above z=0 (glass base slab)
    bevel=0.5,           # rounded bottom-corner radius
    segments=96,         # angular resolution
)

LIQUID = dict(
    fill=0.60,           # default fill fraction (0..1) -> liquid actor Z scale
    inset=0.02,          # tiny gap to the glass inner wall (cm)
)

# ---------------------------------------------------------------------------
# Tweakable parameter contract (MPC)
#   scalars : name -> (default, min, max)
#   vectors : name -> ((r,g,b), description)
# ---------------------------------------------------------------------------
SCALARS = {
    "GlassIOR":          (1.50, 1.00, 2.00),
    "GlassRoughness":    (0.02, 0.00, 0.50),
    "LiquidIOR":         (1.33, 1.00, 2.00),
    "LiquidRoughness":   (0.04, 0.00, 0.50),
    "IceIOR":            (1.31, 1.00, 2.00),
    "IceRoughness":      (0.06, 0.00, 0.50),
    "KeyLightIntensity": (1.00, 0.00, 4.00),
    "RimLightIntensity": (1.00, 0.00, 4.00),
    "ExposureBias":      (0.00, -2.00, 2.00),
}

VECTORS = {
    "LiquidColor":    ((0.52, 0.30, 0.11), "liquid diffuse albedo (amber/whisky)"),
    "LiquidMFP":      ((2.00, 1.00, 0.45), "mean free path cm (short = absorbent)"),
    "GlassTint":      ((1.00, 1.00, 1.00), "glass tint multiplier"),
    "IceColor":       ((0.88, 0.94, 1.00), "ice diffuse albedo"),
    "TableColor":     ((0.17, 0.15, 0.13), "table base color"),
    "BackdropColor":  ((0.52, 0.56, 0.62), "backdrop base color"),
}
