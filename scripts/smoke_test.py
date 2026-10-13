# -*- coding: utf-8 -*-
"""Smoke test: enumerate UE5.8 Python API + verify end-to-end asset creation."""
import sys, os, traceback
import unreal

LOG = []
def log(m): LOG.append(str(m))
def sec(n): LOG.append("\n===== " + n + " =====")

def try_log(fn, label):
    try:
        r = fn()
        log(label + " OK: " + str(r))
        return r
    except Exception as e:
        log(label + " FAIL: " + repr(e))
        return None

log("python " + sys.version)
try_log(lambda: unreal.SystemLibrary.get_engine_version(), "engine version")

sec("SUBSTRATE CLASSES")
try: log(", ".join(sorted(n for n in dir(unreal) if "ubstrate" in n)))
except Exception as e: log("err " + str(e))

sec("MATERIAL EXPRESSION filtered")
try: log(", ".join(sorted(n for n in dir(unreal) if n.startswith("MaterialExpression") and any(k in n for k in ("Transmission","Fresnel","Refraction","Absorption","Slab","ClearCoat","Substrate","Scattering","Media","Heterogeneous")))))
except Exception as e: log("err " + str(e))

sec("MATERIAL EDITING LIBRARY")
try: log(", ".join(sorted(n for n in dir(unreal.MaterialEditingLibrary) if not n.startswith("_"))))
except Exception as e: log("err " + str(e))

sec("STATIC MESH DESCRIPTION methods")
try: log(", ".join(sorted(n for n in dir(unreal.StaticMeshDescription) if not n.startswith("_"))))
except Exception as e: log("err " + str(e))

sec("STATIC MESH build methods")
try: log(", ".join(sorted(n for n in dir(unreal.StaticMesh) if "build_from_mesh" in n or "description" in n.lower())))
except Exception as e: log("err " + str(e))

sec("MPC classes")
try: log(", ".join(sorted(n for n in dir(unreal) if "aterialParameterCollection" in n or "CollectionScalarParameter" in n or "CollectionVectorParameter" in n)))
except Exception as e: log("err " + str(e))

sec("CollectionScalarParameter fields")
try: log(", ".join(sorted(n for n in dir(unreal.CollectionScalarParameter) if not n.startswith("_"))))
except Exception as e: log("err " + str(e))

sec("REMOTE CONTROL")
try: log(", ".join(sorted(n for n in dir(unreal) if "emoteControl" in n)))
except Exception as e: log("err " + str(e))

sec("MATERIAL PROPERTY MP_")
try: log(", ".join(sorted(n for n in dir(unreal.MaterialProperty) if n.startswith("MP_"))))
except Exception as e: log("err " + str(e))

# ---- asset creation tests ----
sec("ASSET CREATION TESTS")
unreal.EditorAssetLibrary.make_directory("/Game/LiquidGlass/Smoke")

def make_mat():
    m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Smoke", "/Game/LiquidGlass/Smoke", unreal.Material, unreal.MaterialFactoryNew())
    return ("created name=" + str(m.get_name())) if m else "None"
try_log(make_mat, "create Material")

def make_mpc():
    fac = unreal.MaterialParameterCollectionFactory()
    mpc = unreal.AssetToolsHelpers.get_asset_tools().create_asset("MPC_Smoke", "/Game/LiquidGlass/Smoke", unreal.MaterialParameterCollection, fac)
    sp = unreal.CollectionScalarParameter()
    sp.parameter_name = "TestScalar"; sp.default_value = 1.0; sp.id = unreal.Guid()
    vp = unreal.CollectionVectorParameter()
    vp.parameter_name = "TestVector"; vp.default_value = unreal.LinearColor(1.0, 0.5, 0.2, 1.0); vp.id = unreal.Guid()
    mpc.set_editor_property("scalar_parameters", [sp])
    mpc.set_editor_property("vector_parameters", [vp])
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke/MPC_Smoke")
    return "scalars=" + str(len(mpc.get_editor_property("scalar_parameters"))) + " vectors=" + str(len(mpc.get_editor_property("vector_parameters")))
try_log(make_mpc, "create MPC")

def make_mesh():
    at = unreal.AssetToolsHelpers.get_asset_tools()
    sm = at.create_asset("SM_Smoke", "/Game/LiquidGlass/Smoke", unreal.StaticMesh, unreal.StaticMeshFactory())
    md = unreal.StaticMeshDescription()
    md.reserve_new_vertices(4); md.reserve_new_vertex_instances(4); md.reserve_new_triangles(2); md.reserve_new_polygon_groups(1)
    pg = md.create_polygon_group()
    pts = [(0,0,0),(10,0,0),(10,10,0),(0,10,0)]
    for i,(x,y,z) in enumerate(pts): md.set_vertex_position(i, unreal.Vector(x,y,z))
    for i in range(4):
        vi = md.create_vertex_instance(i)
        md.set_vertex_instance_uv(vi, unreal.Vector2D(0,0), 0)
    md.create_triangle(pg, [0,1,2]); md.create_triangle(pg, [0,2,3])
    md.compute_polygon_tangents_and_normals([pg])
    method = "none"
    if hasattr(sm, "build_from_mesh_descriptions"):
        sm.build_from_mesh_descriptions([md]); method = "build_from_mesh_descriptions"
    elif hasattr(sm, "build_from_mesh_description"):
        sm.build_from_mesh_description(md); method = "build_from_mesh_description"
    unreal.EditorAssetLibrary.save_asset("/Game/LiquidGlass/Smoke/SM_Smoke")
    return "method=" + method + " verts=" + str(md.get_num_vertex_instances() if hasattr(md,'get_num_vertex_instances') else '?')
try_log(make_mesh, "build static mesh")

try_log(lambda: unreal.EditorAssetLibrary.save_directory("/Game/LiquidGlass/Smoke", True, True), "save directory")

# cleanup smoke assets
try:
    unreal.EditorAssetLibrary.delete_directory("/Game/LiquidGlass/Smoke")
    log("cleanup: deleted /Game/LiquidGlass/Smoke")
except Exception as e:
    log("cleanup FAIL: " + str(e))

out_text = "\n".join(LOG)
os.makedirs(r"D:\ue5\liquied\outputs", exist_ok=True)
with open(r"D:\ue5\liquied\outputs\probe_api.txt", "w", encoding="utf-8") as f:
    f.write(out_text)
print(out_text)
print("SMOKE_DONE")
