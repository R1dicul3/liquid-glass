# -*- coding: utf-8 -*-
"""Probe 5: OBJ export + import as the mesh transport (auto normals)."""
import sys, os, math
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

sec("IMPORT API")
log("ObjFactory exists: " + str(hasattr(unreal, "ObjFactory")))
log("AssetImportTask exists: " + str(hasattr(unreal, "AssetImportTask")))

def make_obj(path):
    """Write a simple lathe cylinder OBJ."""
    R = 2.0; H = 4.0; S = 24
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["# test cylinder"]
    for s in range(S):
        t = 2*math.pi*s/S
        c, sn = math.cos(t), math.sin(t)
        lines.append("v %.5f %.5f %.5f" % (R*c, R*sn, 0.0))       # bottom ring
        lines.append("v %.5f %.5f %.5f" % (R*c, R*sn, H))         # top ring
    for s in range(S):
        lines.append("vt %.5f %.5f" % (s/S, 0.0))
        lines.append("vt %.5f %.5f" % (s/S, 1.0))
    # faces (1-indexed)
    for s in range(S):
        s1 = (s+1) % S
        b0 = 2*s + 1; b1 = 2*s1 + 1
        t0 = 2*s + 2; t1 = 2*s1 + 2
        # side quad: bottom0, bottom1, top1, top0
        lines.append("f %d/%d %d/%d %d/%d" % (b0, b0, b1, b1, t1, t1))
        lines.append("f %d/%d %d/%d %d/%d" % (b0, b0, t1, t1, t0, t0))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log("wrote obj " + path + " (" + str(len(lines)) + " lines)")

def import_obj():
    obj_path = r"D:\ue5\liquied\outputs\mesh_cache\test_cyl.obj"
    make_obj(obj_path)
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", obj_path)
    task.set_editor_property("destination_path", "/Game/LiquidGlass/Smoke5")
    task.set_editor_property("destination_name", "SM_Cyl")
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    task.set_editor_property("replace_existing", True)
    # auto-detect factory from .obj extension (leave factory None)
    unreal.EditorAssetLibrary.make_directory("/Game/LiquidGlass/Smoke5")
    at.import_asset_tasks([task])
    sm = unreal.EditorAssetLibrary.load_asset("/Game/LiquidGlass/Smoke5/SM_Cyl")
    log("imported: " + str(sm is not None) + " class=" + str(sm.get_class().get_name() if sm else "None"))
    if sm:
        # check render data has vertex data
        try:
            log("static_materials count: " + str(len(sm.get_editor_property("static_materials"))))
        except Exception as e:
            log("static_materials read FAIL " + repr(e))
    return "import done"
try_log(import_obj, "OBJ import")

unreal.EditorAssetLibrary.save_directory("/Game/LiquidGlass/Smoke5", True, True)
try:
    unreal.EditorAssetLibrary.delete_directory("/Game/LiquidGlass/Smoke5"); log("cleanup ok")
except Exception as e: log("cleanup FAIL " + str(e))

out_text = "\n".join(LOG)
os.makedirs(r"D:\ue5\liquied\outputs", exist_ok=True)
with open(r"D:\ue5\liquied\outputs\probe5.txt", "w", encoding="utf-8") as f:
    f.write(out_text)
print(out_text)
print("PROBE5_DONE")
