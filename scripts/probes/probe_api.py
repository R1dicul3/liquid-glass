# -*- coding: utf-8 -*-
"""Probe the UE5.8 Python API surface we need, and dump results to outputs/probe_api.txt."""
import sys, os, traceback
import unreal

LOG = []
def log(m):
    LOG.append(str(m))
def section(n):
    LOG.append("\n===== " + n + " =====")

def safe_dir(obj, label):
    try:
        names = [x for x in dir(obj) if not x.startswith("_")]
        log(label + " (" + str(len(names)) + "): " + ", ".join(names))
    except Exception as e:
        log(label + " ERROR: " + str(e))

log("python " + sys.version)
try:
    log("engine version: " + str(unreal.SystemLibrary.get_engine_version()))
except Exception as e:
    log("engine version err: " + str(e))

section("SUBSTRATE CLASSES")
try:
    log("ubstrate: " + ", ".join(sorted(n for n in dir(unreal) if "ubstrate" in n)))
except Exception as e:
    log("err " + str(e))

section("MATERIAL EXPRESSION (filtered)")
try:
    keep = [n for n in dir(unreal) if n.startswith("MaterialExpression") and any(k in n for k in ("Transmission","Fresnel","Refraction","Absorption","Slab","ClearCoat","IOR","Anisotropy","Substrate","Media","Scattering","SSS"))]
    log(", ".join(sorted(keep)))
except Exception as e:
    log("err " + str(e))

section("MATERIAL EDITING LIBRARY")
safe_dir(unreal.MaterialEditingLibrary, "MaterialEditingLibrary")

section("SUBSTRATE-RELATED LIBRARIES")
try:
    su = sorted(n for n in dir(unreal) if "ubstrate" in n and any(k in n for k in ("Library","Utilities","Utility","Function")))
    log("substrate libs: " + ", ".join(su))
    for name in su:
        safe_dir(getattr(unreal, name), name)
except Exception as e:
    log("err " + str(e))

section("STATIC MESH DESCRIPTION")
safe_dir(unreal.StaticMeshDescription, "StaticMeshDescription")

section("MPC / PARAM COLLECTION")
try:
    log("mpc: " + ", ".join(sorted(n for n in dir(unreal) if "aterialParameterCollection" in n)))
except Exception as e:
    log("err " + str(e))

section("REMOTE CONTROL")
try:
    log("rc: " + ", ".join(sorted(n for n in dir(unreal) if "emoteControl" in n)))
except Exception as e:
    log("err " + str(e))

section("MATERIAL PROPERTY ENUM (MP_)")
try:
    log(", ".join(sorted(n for n in dir(unreal.MaterialProperty) if n.startswith("MP_"))))
except Exception as e:
    log("err " + str(e))

section("FACTORIES (filtered)")
try:
    log(", ".join(sorted(n for n in dir(unreal) if n.endswith("Factory") and any(k in n for k in ("Material","StaticMesh","ParameterCollection")))))
except Exception as e:
    log("err " + str(e))

section("EDITOR ASSET LIBRARY")
safe_dir(unreal.EditorAssetLibrary, "EditorAssetLibrary")

section("ASSET TOOLS")
safe_dir(unreal.AssetToolsHelpers, "AssetToolsHelpers")

out_text = "\n".join(LOG)
os.makedirs(r"D:\ue5\liquied\outputs", exist_ok=True)
with open(r"D:\ue5\liquied\outputs\probe_api.txt", "w", encoding="utf-8") as f:
    f.write(out_text)
print(out_text)
print("PROBE_DONE")
try:
    unreal.SystemLibrary.quit_editor()
except Exception:
    pass
