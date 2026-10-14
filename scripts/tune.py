# -*- coding: utf-8 -*-
"""Apply configs/tuning.json -> MPC (materials) + actors (lights / fill / exposure).

Run live in the editor to tweak by eye:
    py scripts/tune.py
"""
import json
import os
import unreal
import params as P
import common as C

DEFAULT_JSON = os.path.join(C.REPO_ROOT, "configs", "tuning.json")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _set_mpc(mpc, scalars, vectors):
    if scalars:
        params = mpc.get_editor_property("scalar_parameters")
        for sp in params:
            name = sp.get_editor_property("parameter_name")
            if name in scalars:
                sp.set_editor_property("default_value", float(scalars[name]))
        mpc.set_editor_property("scalar_parameters", params)
    if vectors:
        params = mpc.get_editor_property("vector_parameters")
        for vp in params:
            name = vp.get_editor_property("parameter_name")
            if name in vectors:
                v = vectors[name]
                vp.set_editor_property("default_value", unreal.LinearColor(v[0], v[1], v[2], 1.0))
        mpc.set_editor_property("vector_parameters", params)
    C.save_asset(P.MPC)


def _find_actor(label):
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a is not None and a.get_actor_label() == label:
            return a
    return None


def _set_light_intensity(label, value):
    a = _find_actor(label)
    if a is None:
        C.log("actor not found: " + label); return
    comps = a.get_components_by_class(unreal.LightComponentBase) if hasattr(a, "get_components_by_class") else None
    if comps:
        for c in comps:
            if hasattr(c, "set_editor_property"):
                c.set_editor_property("intensity", float(value))
    else:
        c = a.get_component_by_class(unreal.LightComponentBase)
        if c:
            c.set_editor_property("intensity", float(value))


def apply(path=DEFAULT_JSON):
    C.log("=== tune: " + path + " ===")
    data = _load_json(path)
    mpc = C.load_asset(P.MPC)
    if mpc is None:
        C.log("MPC missing"); return

    _set_mpc(mpc, data.get("scalars"), data.get("vectors"))

    actor = data.get("actor", {})
    if "LiquidFill" in actor:
        a = _find_actor("Liquid")
        if a:
            fill = float(actor["LiquidFill"])
            a.set_actor_scale3d(unreal.Vector(1.0, 1.0, fill))
            C.log("LiquidFill -> " + str(fill))

    sc = data.get("scalars", {})
    if "KeyLightIntensity" in sc:
        _set_light_intensity("KeyLight", 3.0 * float(sc["KeyLightIntensity"]))
    if "RimLightIntensity" in sc:
        _set_light_intensity("RimRect", 6.0 * float(sc["RimLightIntensity"]))
    if "ExposureBias" in sc:
        ppv = _find_actor("PostProcess")
        if ppv:
            try:
                s = ppv.get_editor_property("settings")
                s.set_editor_property("auto_exposure_bias", float(sc["ExposureBias"]))
                ppv.set_editor_property("settings", s)
            except Exception as e:
                C.log("exposure set FAIL " + repr(e))
    C.log("=== tune done ===")


if __name__ == "__main__":
    apply()
