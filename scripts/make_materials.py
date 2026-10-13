# -*- coding: utf-8 -*-
"""Build Substrate materials (glass / liquid / ice / stone / table / backdrop).

All materials read tweakable parameters from the MPC via
MaterialExpressionCollectionParameter nodes. F0 is derived from IOR in-graph:
F0 = ((IOR-1)/(IOR+1))^2  (Schlick reflectance at normal incidence).
"""
import unreal
import params as P
import common as C

MEL = unreal.MaterialEditingLibrary


def _node(m, cls, x, y):
    return MEL.create_material_expression(m, cls, x, y)


def _constant(m, value, x, y):
    e = _node(m, unreal.MaterialExpressionConstant, x, y)
    e.set_editor_property("r", float(value))
    return e


def _const3(m, r, g, b, x, y):
    e = _node(m, unreal.MaterialExpressionConstant3Vector, x, y)
    e.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))
    return e


def _mpc_param(m, mpc, name, x, y):
    e = _node(m, unreal.MaterialExpressionCollectionParameter, x, y)
    e.set_editor_property("collection", mpc)
    e.set_editor_property("parameter_name", name)
    return e


def _connect(m, a, b, b_in):
    outs = MEL.get_material_expression_output_names(a)
    out_name = outs[0] if outs else ""
    ok = MEL.connect_material_expressions(a, out_name, b, b_in)
    if not ok:
        C.log("  connect FAIL: (%s)->(%s.%s)" % (a.get_name(), b.get_name(), b_in))
    return ok


def _f0_from_ior(m, ior_expr, x, y):
    one = _constant(m, 1.0, x, y + 120)
    sub = _node(m, unreal.MaterialExpressionSubtract, x + 220, y)
    _connect(m, ior_expr, sub, "A"); _connect(m, one, sub, "B")
    add = _node(m, unreal.MaterialExpressionAdd, x + 220, y + 160)
    _connect(m, ior_expr, add, "A"); _connect(m, one, add, "B")
    div = _node(m, unreal.MaterialExpressionDivide, x + 440, y)
    _connect(m, sub, div, "A"); _connect(m, add, div, "B")
    sq = _node(m, unreal.MaterialExpressionMultiply, x + 660, y)
    _connect(m, div, sq, "A"); _connect(m, div, sq, "B")
    return sq


def _mul_scalar(m, expr, scalar, x, y):
    c = _constant(m, scalar, x, y)
    mul = _node(m, unreal.MaterialExpressionMultiply, x + 200, y)
    _connect(m, expr, mul, "A"); _connect(m, c, mul, "B")
    return mul


def _new_material(path, blend_mode=None):
    name = path.rsplit("/", 1)[1]
    pkg = path.rsplit("/", 1)[0]
    if C.asset_exists(path):
        C.delete_asset(path)
    C.ensure_dir(pkg)
    m = C.create_asset(name, pkg, unreal.Material, unreal.MaterialFactoryNew())
    if m is None:
        C.log("FAILED create material " + path); return None
    if blend_mode is not None:
        m.set_editor_property("blend_mode", blend_mode)
    return m


def _finish(m, slab, path):
    outs = MEL.get_material_expression_output_names(slab)
    ok = MEL.connect_material_property(slab, outs[0], unreal.MaterialProperty.MP_FRONT_MATERIAL)
    MEL.recompile_material(m)
    C.save_asset(path)
    C.log("Built material " + path + " (front=" + str(ok) + ")")
    return m


T = unreal.BlendMode.BLEND_TRANSLUCENT
O = unreal.BlendMode.BLEND_OPAQUE


def make_glass(mpc):
    m = _new_material(P.M_GLASS, T)
    slab = _node(m, unreal.MaterialExpressionSubstrateSlabBSDF, -500, 0)
    ior = _mpc_param(m, mpc, "GlassIOR", -900, -300)
    f0 = _f0_from_ior(m, ior, -900, -300)
    _connect(m, f0, slab, "F0")
    _connect(m, _mpc_param(m, mpc, "GlassRoughness", -900, 0), slab, "Roughness")
    tint = _mpc_param(m, mpc, "GlassTint", -900, 220)
    _connect(m, _mul_scalar(m, tint, 0.02, -680, 220), slab, "Diffuse Albedo")
    return _finish(m, slab, P.M_GLASS)


def make_liquid(mpc):
    m = _new_material(P.M_LIQUID, T)
    slab = _node(m, unreal.MaterialExpressionSubstrateSlabBSDF, -500, 0)
    ior = _mpc_param(m, mpc, "LiquidIOR", -900, -300)
    f0 = _f0_from_ior(m, ior, -900, -300)
    _connect(m, f0, slab, "F0")
    _connect(m, _mpc_param(m, mpc, "LiquidRoughness", -900, 0), slab, "Roughness")
    _connect(m, _mpc_param(m, mpc, "LiquidColor", -900, 200), slab, "Diffuse Albedo")
    _connect(m, _mpc_param(m, mpc, "LiquidMFP", -900, 400), slab, "SSS MFP")
    return _finish(m, slab, P.M_LIQUID)


def make_ice(mpc):
    m = _new_material(P.M_ICE, T)
    slab = _node(m, unreal.MaterialExpressionSubstrateSlabBSDF, -500, 0)
    ior = _mpc_param(m, mpc, "IceIOR", -900, -300)
    f0 = _f0_from_ior(m, ior, -900, -300)
    _connect(m, f0, slab, "F0")
    _connect(m, _mpc_param(m, mpc, "IceRoughness", -900, 0), slab, "Roughness")
    ice_color = _mpc_param(m, mpc, "IceColor", -900, 220)
    _connect(m, _mul_scalar(m, ice_color, 0.3, -680, 220), slab, "Diffuse Albedo")
    _connect(m, _const3(m, 10.0, 10.0, 10.0, -900, 420), slab, "SSS MFP")
    return _finish(m, slab, P.M_ICE)


def make_stone(mpc):
    m = _new_material(P.M_STONE, O)
    slab = _node(m, unreal.MaterialExpressionSubstrateSlabBSDF, -500, 0)
    _connect(m, _constant(m, 0.04, -900, -200), slab, "F0")
    _connect(m, _constant(m, 0.20, -900, 0), slab, "Roughness")
    _connect(m, _const3(m, 0.08, 0.08, 0.09, -900, 200), slab, "Diffuse Albedo")
    return _finish(m, slab, P.M_STONE)


def make_table(mpc):
    m = _new_material(P.M_TABLE, O)
    slab = _node(m, unreal.MaterialExpressionSubstrateSlabBSDF, -500, 0)
    _connect(m, _constant(m, 0.04, -900, -200), slab, "F0")
    _connect(m, _constant(m, 0.35, -900, 0), slab, "Roughness")
    _connect(m, _mpc_param(m, mpc, "TableColor", -900, 200), slab, "Diffuse Albedo")
    return _finish(m, slab, P.M_TABLE)


def make_backdrop(mpc):
    m = _new_material(P.M_BACKDROP, O)
    slab = _node(m, unreal.MaterialExpressionSubstrateSlabBSDF, -500, 0)
    _connect(m, _constant(m, 0.04, -900, -200), slab, "F0")
    _connect(m, _constant(m, 0.60, -900, 0), slab, "Roughness")
    _connect(m, _mpc_param(m, mpc, "BackdropColor", -900, 200), slab, "Diffuse Albedo")
    return _finish(m, slab, P.M_BACKDROP)


def run():
    C.log("=== make_materials ===")
    mpc = C.load_asset(P.MPC)
    if mpc is None:
        C.log("MPC missing - run make_mpc first"); return
    make_glass(mpc)
    make_liquid(mpc)
    make_ice(mpc)
    make_stone(mpc)
    make_table(mpc)
    make_backdrop(mpc)
    C.log("=== make_materials done ===")


if __name__ == "__main__":
    run()
