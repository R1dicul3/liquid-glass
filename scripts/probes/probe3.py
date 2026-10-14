# -*- coding: utf-8 -*-
"""Probe 3: exact factory names, struct field names, Substrate pins (single-arg)."""
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

# ---------- factories ----------
sec("FACTORIES")
log("mesh/material/param factories: " + ", ".join(sorted(n for n in dir(unreal) if n.endswith("Factory") and any(k in n for k in ("Mesh","Material","Parameter","Texture")))))

# ---------- struct field discovery ----------
sec("STRUCT FIELDS")
sp = unreal.CollectionScalarParameter()
log("scalar to_dict: " + str(sp.to_dict()))
try: log("scalar export_text: " + str(sp.export_text()))
except Exception as e: log("scalar export_text FAIL " + repr(e))
vp = unreal.CollectionVectorParameter()
log("vector to_dict: " + str(vp.to_dict()))
try:
    sp2 = unreal.CollectionScalarParameter(parameter_name="X", default_value=2.0)
    log("kwargs scalar: " + str(sp2.to_dict()))
except Exception as e:
    log("kwargs scalar FAIL: " + repr(e))

# ---------- Substrate pins (single-arg) ----------
sec("SUBSTRATE PINS (single arg)")
at = unreal.AssetToolsHelpers.get_asset_tools()
unreal.EditorAssetLibrary.make_directory("/Game/LiquidGlass/Smoke3")
m = at.create_asset("M_Pin", "/Game/LiquidGlass/Smoke3", unreal.Material, unreal.MaterialFactoryNew())
MEL = unreal.MaterialEditingLibrary
for cls_name in ["SubstrateSlabBSDF", "SubstrateSingleLayerWaterBSDF", "SubstrateSimpleClearCoatBSDF",
                 "SubstrateHorizontalMixing", "SubstrateTransmittanceToMFP"]:
    cls = getattr(unreal, "MaterialExpression" + cls_name, None)
    if cls is None: log(cls_name + " CLASS MISSING"); continue
    try:
        e = MEL.create_material_expression(m, cls, -800, 0)
        ins = MEL.get_material_expression_input_names(e)
        outs = MEL.get_material_expression_output_names(e)
        types = MEL.get_material_expression_input_types(e)
        log(cls_name + " IN=" + str(list(ins)))
        log(cls_name + " OUT=" + str(list(outs)))
        log(cls_name + " TYPES=" + str(list(types)))
    except Exception as ex:
        log(cls_name + " ERR: " + repr(ex))

# ---------- slab settable properties ----------
sec("SLAB PROPERTIES")
try:
    e = MEL.create_material_expression(m, unreal.MaterialExpressionSubstrateSlabBSDF, -800, 100)
    for p in ["diffuse_color","f0","roughness","normal","second_roughness","anisotropy","refraction","top_material","sss_mfp","emissive","fuzz_color","glint"]:
        try: log("slab." + p + " = " + str(e.get_editor_property(p)))
        except Exception: log("slab." + p + " MISSING")
    # also try set refraction directly
    try:
        e.set_editor_property("refraction", 1.5); log("set refraction OK -> " + str(e.get_editor_property("refraction")))
    except Exception as ex:
        log("set refraction FAIL " + repr(ex))
except Exception as ex:
    log("slab create FAIL " + repr(ex))

# ---------- minimal Substrate material end-to-end ----------
sec("MINIMAL SUBSTRATE MATERIAL")
def make_min_mat():
    mm = at.create_asset("M_MinSub", "/Game/LiquidGlass/Smoke3", unreal.Material, unreal.MaterialFactoryNew())
    slab = MEL.create_material_expression(mm, unreal.MaterialExpressionSubstrateSlabBSDF, -400, 0)
    # try to connect slab output -> front material
    outs = MEL.get_material_expression_output_names(slab)
    log("slab outputs: " + str(list(outs)))
    ok = MEL.connect_material_property(slab, outs[0], unreal.MaterialProperty.MP_FRONT_MATERIAL)
    log("connect to MP_FRONT_MATERIAL -> " + str(ok))
    MEL.recompile_material(mm)
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke3/M_MinSub")
    return "connected=" + str(ok)
try_log(make_min_mat, "minimal substrate material")

# ---------- static mesh with correct factory ----------
sec("STATIC MESH (factory discover)")
def make_mesh():
    fac = None
    for name in ["StaticMeshFactory", "StaticMeshFactoryNew"]:
        if hasattr(unreal, name):
            fac = getattr(unreal, name)(); log("using factory " + name); break
    if fac is None:
        sm = at.create_asset("SM_T", "/Game/LiquidGlass/Smoke3", unreal.StaticMesh, None)
        log("created with None factory: " + str(sm is not None))
    else:
        sm = at.create_asset("SM_T", "/Game/LiquidGlass/Smoke3", unreal.StaticMesh, fac)
    md = unreal.StaticMeshDescription()
    has_reserve = hasattr(md, "reserve_new_vertices")
    log("has reserve_new_vertices: " + str(has_reserve))
    if has_reserve:
        md.reserve_new_vertices(4); md.reserve_new_vertex_instances(4); md.reserve_new_triangles(2); md.reserve_new_polygon_groups(1)
    pg = md.create_polygon_group()
    pts = [(0,0,0),(10,0,0),(10,10,0),(0,10,0)]
    if has_reserve:
        for i,(x,y,z) in enumerate(pts): md.set_vertex_position(i, unreal.Vector(x,y,z))
        vids = [0,1,2,3]
    else:
        vids = []
        for (x,y,z) in pts:
            v = md.create_vertex(); md.set_vertex_position(v, unreal.Vector(x,y,z)); vids.append(v)
    for v in vids:
        vi = md.create_vertex_instance(v)
        md.set_vertex_instance_uv(vi, unreal.Vector2D(0,0), 0)
    md.create_triangle(pg, vids[0:3]); md.create_triangle(pg, [vids[0], vids[2], vids[3]])
    md.compute_polygon_tangents_and_normals([pg])
    sm.build_from_static_mesh_descriptions([md])
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke3/SM_T")
    return "verts=" + str(md.get_vertex_count())
try_log(make_mesh, "static mesh")

unreal.EditorAssetLibrary.save_directory("/Game/LiquidGlass/Smoke3", True, True)
try:
    unreal.EditorAssetLibrary.delete_directory("/Game/LiquidGlass/Smoke3"); log("cleanup ok")
except Exception as e: log("cleanup FAIL " + str(e))

out_text = "\n".join(LOG)
os.makedirs(r"D:\ue5\liquied\outputs", exist_ok=True)
with open(r"D:\ue5\liquied\outputs\probe3.txt", "w", encoding="utf-8") as f:
    f.write(out_text)
print(out_text)
print("PROBE3_DONE")
