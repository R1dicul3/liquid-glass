# -*- coding: utf-8 -*-
"""Probe 4: mesh vertex ID API, MPC struct setting, full Substrate material (translucent + opaque)."""
import sys, os
import unreal

LOG = []
def log(m): LOG.append(str(m))
def sec(n): LOG.append("\n===== " + n + " =====")
def try_log(fn, label):
    try:
        r = fn(); log(label + " OK: " + str(r)); return r
    except Exception as e:
        log(label + " FAIL: " + repr(e)); return None

log("python " + sys.version)
at = unreal.AssetToolsHelpers.get_asset_tools()
unreal.EditorAssetLibrary.make_directory("/Game/LiquidGlass/Smoke4")

# ---------- mesh vertex ID API ----------
sec("MESH VERTEX API")
def make_mesh():
    sm = at.create_asset("SM_T", "/Game/LiquidGlass/Smoke4", unreal.StaticMesh, None)
    md = unreal.StaticMeshDescription()
    pg = md.create_polygon_group()
    pts = [(0,0,0),(10,0,0),(10,10,0),(0,10,0)]
    vids = []
    for (x,y,z) in pts:
        v = md.create_vertex()
        md.set_vertex_position(v, unreal.Vector(x,y,z))
        vids.append(v)
    log("vertex id type: " + str(type(vids[0])) + " = " + str(vids[0]))
    insts = []
    for v in vids:
        vi = md.create_vertex_instance(v)
        md.set_vertex_instance_uv(vi, unreal.Vector2D(0,0), 0)
        insts.append(vi)
    md.create_triangle(pg, [insts[0], insts[1], insts[2]])
    md.create_triangle(pg, [insts[0], insts[2], insts[3]])
    md.compute_polygon_tangents_and_normals([pg])
    sm.build_from_static_mesh_descriptions([md])
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke4/SM_T")
    return "verts=" + str(md.get_vertex_count()) + " tris=" + str(md.get_triangle_count())
try_log(make_mesh, "mesh via create_vertex")

# ---------- MPC struct setting ----------
sec("MPC STRUCT SETTING")
def test_mpc():
    sp = unreal.CollectionScalarParameter()
    results = []
    # try many field-setting approaches
    for mode, fn in [
        ("snake_set", lambda: sp.set_editor_property("default_value", 1.5)),
        ("pascal_set", lambda: sp.set_editor_property("DefaultValue", 1.5)),
        ("snake_attr", lambda: setattr(sp, "default_value", 1.5)),
        ("pascal_attr", lambda: setattr(sp, "DefaultValue", 1.5)),
    ]:
        try:
            fn(); results.append(mode + "=ok")
        except Exception as e:
            results.append(mode + "=" + type(e).__name__)
    log("field set results: " + str(results))
    # read back via export_text + to_dict
    log("export_text after: " + str(sp.export_text()))
    log("to_dict after: " + str(sp.to_dict()))
    # import_text approach
    sp2 = unreal.CollectionScalarParameter()
    try:
        sp2.import_text('(DefaultValue=2.500000,ParameterName="S_Imp",Id=00000000000000000000000000000001)')
        log("import_text ok -> " + str(sp2.export_text()))
    except Exception as e:
        log("import_text FAIL " + repr(e))
    return str(results)
try_log(test_mpc, "mpc struct")

# now actually build an MPC with two params using the BEST approach (snake_set via set_editor_property)
def build_mpc():
    fac = unreal.MaterialParameterCollectionFactoryNew()
    mpc = at.create_asset("MPC_T", "/Game/LiquidGlass/Smoke4", unreal.MaterialParameterCollection, fac)
    sp = unreal.CollectionScalarParameter()
    sp.set_editor_property("default_value", 1.5)
    sp.set_editor_property("parameter_name", "S_A")
    vp = unreal.CollectionVectorParameter()
    vp.set_editor_property("default_value", unreal.LinearColor(1,0.5,0.2,1))
    vp.set_editor_property("parameter_name", "V_A")
    mpc.set_editor_property("scalar_parameters", [sp])
    mpc.set_editor_property("vector_parameters", [vp])
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke4/MPC_T")
    mpc2 = unreal.EditorAssetLibrary.load_asset("/Game/LiquidGlass/Smoke4/MPC_T")
    sc = mpc2.get_editor_property("scalar_parameters")
    log("scalar count=" + str(len(sc)) + " name=" + str(sc[0].get_editor_property("parameter_name")) + " val=" + str(sc[0].get_editor_property("default_value")))
    return "mpc built"
try_log(build_mpc, "mpc build")

# ---------- Substrate material: translucent glass ----------
sec("SUBSTRATE MATERIAL (translucent + opaque)")
MEL = unreal.MaterialEditingLibrary
def make_glass():
    m = at.create_asset("M_GlassT", "/Game/LiquidGlass/Smoke4", unreal.Material, unreal.MaterialFactoryNew())
    # blend mode
    try:
        m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        log("set blend_mode translucent OK; readback=" + str(m.get_editor_property("blend_mode")))
    except Exception as e:
        log("set blend_mode FAIL " + repr(e))
    slab = MEL.create_material_expression(m, unreal.MaterialExpressionSubstrateSlabBSDF, -600, 0)
    # F0 constant (0.04 for IOR 1.5)
    f0 = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -800, -200)
    f0.set_editor_property("r", 0.04)
    rough = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -800, 0)
    rough.set_editor_property("r", 0.02)
    diffuse = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -800, 200)
    diffuse.set_editor_property("constant", unreal.LinearColor(0.02,0.02,0.02,1))
    MEL.connect_material_expressions(f0, "", slab, "F0")
    MEL.connect_material_expressions(rough, "", slab, "Roughness")
    MEL.connect_material_expressions(diffuse, "", slab, "Diffuse Albedo")
    outs = MEL.get_material_expression_output_names(slab)
    ok = MEL.connect_material_property(slab, outs[0], unreal.MaterialProperty.MP_FRONT_MATERIAL)
    MEL.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke4/M_GlassT")
    return "connected=" + str(ok) + " blend=" + str(m.get_editor_property("blend_mode"))
try_log(make_glass, "glass material")

def make_stone():
    m = at.create_asset("M_StoneT", "/Game/LiquidGlass/Smoke4", unreal.Material, unreal.MaterialFactoryNew())
    slab = MEL.create_material_expression(m, unreal.MaterialExpressionSubstrateSlabBSDF, -600, 0)
    f0 = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -800, -200); f0.set_editor_property("r", 0.04)
    rough = MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -800, 0); rough.set_editor_property("r", 0.3)
    diffuse = MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -800, 200); diffuse.set_editor_property("constant", unreal.LinearColor(0.2,0.18,0.16,1))
    MEL.connect_material_expressions(f0, "", slab, "F0")
    MEL.connect_material_expressions(rough, "", slab, "Roughness")
    MEL.connect_material_expressions(diffuse, "", slab, "Diffuse Albedo")
    outs = MEL.get_material_expression_output_names(slab)
    ok = MEL.connect_material_property(slab, outs[0], unreal.MaterialProperty.MP_FRONT_MATERIAL)
    MEL.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke4/M_StoneT")
    return "opaque connected=" + str(ok)
try_log(make_stone, "opaque material")

unreal.EditorAssetLibrary.save_directory("/Game/LiquidGlass/Smoke4", True, True)
try:
    unreal.EditorAssetLibrary.delete_directory("/Game/LiquidGlass/Smoke4"); log("cleanup ok")
except Exception as e: log("cleanup FAIL " + str(e))

out_text = "\n".join(LOG)
os.makedirs(r"D:\ue5\liquied\outputs", exist_ok=True)
with open(r"D:\ue5\liquied\outputs\probe4.txt", "w", encoding="utf-8") as f:
    f.write(out_text)
print(out_text)
print("PROBE4_DONE")
