# -*- coding: utf-8 -*-
"""Probe 2: Substrate BSDF input pins + mesh/MPC ground-truth paths."""
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

# ---------- Substrate expression input/output pins ----------
sec("SUBSTRATE BSDF PINS")
nodes = ["SubstrateSlabBSDF", "SubstrateSingleLayerWaterBSDF", "SubstrateSimpleClearCoatBSDF",
         "SubstrateHorizontalMixing", "SubstrateWeight", "SubstrateTransmittanceToMFP",
         "SubstrateVerticalLayering", "SubstrateAdd"]
at = unreal.AssetToolsHelpers.get_asset_tools()
m = at.create_asset("M_Pin", "/Game/LiquidGlass/Smoke2", unreal.Material, unreal.MaterialFactoryNew())
unreal.EditorAssetLibrary.make_directory("/Game/LiquidGlass/Smoke2")
MEL = unreal.MaterialEditingLibrary
for cls_name in nodes:
    cls = getattr(unreal, "MaterialExpression" + cls_name, None)
    if cls is None:
        log(cls_name + ": CLASS MISSING"); continue
    try:
        e = MEL.create_material_expression(m, cls, -800, 0)
        ins = MEL.get_material_expression_input_names(m, e)
        outs = MEL.get_material_expression_output_names(m, e)
        types = MEL.get_material_expression_input_types(m, e)
        log(cls_name + " IN=" + str(list(ins)) + " OUT=" + str(list(outs)) + " TYPES=" + str(list(types)))
    except Exception as ex:
        log(cls_name + " ERR: " + repr(ex))

# ---------- CollectionParameter expression ----------
sec("COLLECTION PARAMETER EXPR")
try:
    ce = MEL.create_material_expression(m, unreal.MaterialExpressionCollectionParameter, -800, 200)
    log("CollectionParameter dir: " + ", ".join(sorted(n for n in dir(ce) if not n.startswith("_"))))
    for prop in ["collection", "parameter_name", "default_value"]:
        try: log("  prop " + prop + " = " + str(ce.get_editor_property(prop)))
        except Exception as e: log("  prop " + prop + " ERR " + str(e))
except Exception as e:
    log("CollectionParameter ERR " + repr(e))

# ---------- scalar/vector param expressions ----------
sec("PARAM EXPRESSIONS")
for cls_name in ["ScalarParameter", "VectorParameter", "Constant", "Constant3Vector", "Constant4Vector"]:
    try:
        cls = getattr(unreal, "MaterialExpression" + cls_name)
        e = MEL.create_material_expression(m, cls, -800, 400)
        props = {}
        for p in ["parameter_name", "default_value", "r", "g", "b", "a"]:
            try: props[p] = str(e.get_editor_property(p))
            except Exception: pass
        log(cls_name + " -> " + str(props))
    except Exception as e:
        log(cls_name + " ERR " + repr(e))

# ---------- MPC creation (correct factory) ----------
sec("MPC CREATION")
def make_mpc():
    fac = unreal.MaterialParameterCollectionFactoryNew()
    mpc = at.create_asset("MPC_T", "/Game/LiquidGlass/Smoke2", unreal.MaterialParameterCollection, fac)
    sp = unreal.CollectionScalarParameter()
    try:
        sp.set_editor_property("parameter_name", "S_Test")
        sp.set_editor_property("default_value", 1.5)
        sp.set_editor_property("id", unreal.Guid())
        mode = "set_editor_property"
    except Exception:
        sp.parameter_name = "S_Test"; sp.default_value = 1.5; sp.id = unreal.Guid(); mode = "attr"
    vp = unreal.CollectionVectorParameter()
    try:
        vp.set_editor_property("parameter_name", "V_Test")
        vp.set_editor_property("default_value", unreal.LinearColor(1,0.5,0.2,1))
        vp.set_editor_property("id", unreal.Guid())
    except Exception:
        vp.parameter_name = "V_Test"; vp.default_value = unreal.LinearColor(1,0.5,0.2,1); vp.id = unreal.Guid()
    mpc.set_editor_property("scalar_parameters", [sp])
    mpc.set_editor_property("vector_parameters", [vp])
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke2/MPC_T")
    mpc2 = unreal.EditorAssetLibrary.load_asset("/Game/LiquidGlass/Smoke2/MPC_T")
    sc = mpc2.get_editor_property("scalar_parameters")
    vc = mpc2.get_editor_property("vector_parameters")
    return "mode=" + mode + " scalars=" + str(len(sc)) + " vec=" + str(len(vc)) + " sname=" + str(sc[0].get_editor_property("parameter_name") if sc else "?")
try_log(make_mpc, "MPC")

# ---------- static mesh build (final path) ----------
sec("STATIC MESH BUILD")
def make_mesh():
    sm = at.create_asset("SM_T", "/Game/LiquidGlass/Smoke2", unreal.StaticMesh, unreal.StaticMeshFactory())
    md = unreal.StaticMeshDescription()
    has_reserve = hasattr(md, "reserve_new_vertices")
    if has_reserve:
        md.reserve_new_vertices(4); md.reserve_new_vertex_instances(4); md.reserve_new_triangles(2); md.reserve_new_polygon_groups(1)
    pg = md.create_polygon_group()
    pts = [(0,0,0),(10,0,0),(10,10,0),(0,10,0)]
    vids = []
    if hasattr(md, "create_vertex") and not has_reserve:
        for (x,y,z) in pts:
            v = md.create_vertex(); md.set_vertex_position(v, unreal.Vector(x,y,z)); vids.append(v)
    else:
        for i,(x,y,z) in enumerate(pts):
            md.set_vertex_position(i, unreal.Vector(x,y,z)); vids.append(i)
    for v in vids:
        vi = md.create_vertex_instance(v)
        md.set_vertex_instance_uv(vi, unreal.Vector2D(0,0), 0)
    md.create_triangle(pg, [0,1,2]); md.create_triangle(pg, [0,2,3])
    md.compute_polygon_tangents_and_normals([pg])
    sm.build_from_static_mesh_descriptions([md])
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke2/SM_T")
    return "reserve=" + str(has_reserve) + " verts=" + str(md.get_vertex_count())
try_log(make_mesh, "mesh")

# ---------- recompile ----------
sec("RECOMPILE")
try_log(lambda: MEL.recompile_material(m), "recompile_material")

unreal.EditorAssetLibrary.save_directory("/Game/LiquidGlass/Smoke2", True, True)
try:
    unreal.EditorAssetLibrary.delete_directory("/Game/LiquidGlass/Smoke2")
    log("cleanup ok")
except Exception as e:
    log("cleanup FAIL " + str(e))

out_text = "\n".join(LOG)
os.makedirs(r"D:\ue5\liquied\outputs", exist_ok=True)
with open(r"D:\ue5\liquied\outputs\probe2.txt", "w", encoding="utf-8") as f:
    f.write(out_text)
print(out_text)
print("PROBE2_DONE")
