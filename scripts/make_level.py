# -*- coding: utf-8 -*-
"""Assemble the demo level: meshes, lights, camera, post-process. Idempotent-ish."""
import math
import unreal
import params as P
import common as C

BASIC = {
    "cube": "/Engine/BasicShapes/Cube.Cube",
    "sphere": "/Engine/BasicShapes/Sphere.Sphere",
    "plane": "/Engine/BasicShapes/Plane.Plane",
    "cylinder": "/Engine/BasicShapes/Cylinder.Cylinder",
}


def _look_at(loc, target):
    try:
        return unreal.MathLibrary.find_look_at_rotation(loc, target)
    except Exception:
        return unreal.Rotator(0.0, 0.0, 0.0)


def _spawn(cls, loc, rot=unreal.Rotator(0, 0, 0), label=""):
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, rot)
    if actor is None:
        C.log("SPAWN FAIL " + str(cls)); return None
    if label:
        actor.set_actor_label(label)
    return actor


def _spawn_mesh(mesh_path, mat_path, loc, rot, scale, label):
    actor = _spawn(unreal.StaticMeshActor.static_class(), loc, rot, label)
    if actor is None:
        return None
    smc = actor.get_component_by_class(unreal.StaticMeshComponent)
    if smc is None:
        smc = actor.static_mesh_component
    if mesh_path and C.asset_exists(mesh_path):
        smc.set_static_mesh(C.load_asset(mesh_path))
    if mat_path and C.asset_exists(mat_path):
        smc.set_material(0, C.load_asset(mat_path))
    actor.set_actor_scale3d(unreal.Vector(scale[0], scale[1], scale[2]))
    return actor


def _light_component(actor):
    for cls in (unreal.DirectionalLightComponent, unreal.RectLightComponent,
                unreal.SkyLightComponent, unreal.PointLightComponent):
        c = actor.get_component_by_class(cls)
        if c is not None:
            return c
    return None


def place_scene():
    origin = unreal.Vector(0, 0, 0)

    # table (top surface at z=0)
    _spawn_mesh(BASIC["cube"], P.M_TABLE, unreal.Vector(0, 0, -1.0), unreal.Rotator(0, 0, 0),
                (80.0, 80.0, 2.0), "Table")

    # backdrop (vertical plane behind the glass, facing +Y)
    _spawn_mesh(BASIC["plane"], P.M_BACKDROP, unreal.Vector(0, -70, 45), unreal.Rotator(0, 0, -90),
                (160.0, 100.0, 1.0), "Backdrop")

    # glass + liquid
    _spawn_mesh(P.SM_TUMBLER, P.M_GLASS, origin, unreal.Rotator(0, 0, 0), (1.0, 1.0, 1.0), "Glass")
    tb, liq = P.TUMBLER, P.LIQUID
    base = tb["base"]
    _spawn_mesh(P.SM_LIQUID, P.M_LIQUID, unreal.Vector(0, 0, base), unreal.Rotator(0, 0, 0),
                (1.0, 1.0, liq["fill"]), "Liquid")

    # objects inside the liquid
    inner_top = (tb["height"] - tb["wall"]) - base
    liq_top = base + liq["fill"] * inner_top
    # ice cube (floating near the surface)
    _spawn_mesh(BASIC["cube"], P.M_ICE, unreal.Vector(-0.4, 0.3, liq_top - 1.3),
                unreal.Rotator(12, 28, 8), (2.1, 2.1, 2.1), "Ice")
    # whisky stone (resting on the inner bottom)
    _spawn_mesh(BASIC["sphere"], P.M_STONE, unreal.Vector(0.7, -0.4, base + 0.9),
                unreal.Rotator(0, 0, 0), (1.7, 1.7, 1.7), "Stone")


def place_lights():
    d = P.SCALAR_DEFAULTS if hasattr(P, "SCALAR_DEFAULTS") else {k: v[0] for k, v in P.SCALARS.items()}
    key_i = d.get("KeyLightIntensity", 1.0)
    rim_i = d.get("RimLightIntensity", 1.0)

    # key directional light (sun-like)
    dl = _spawn(unreal.DirectionalLight.static_class(), unreal.Vector(-40, -30, 80),
                _look_at(unreal.Vector(-40, -30, 80), unreal.Vector(0, 0, 20)), "KeyLight")
    if dl:
        c = _light_component(dl)
        c.set_editor_property("intensity", 3.0 * key_i)
        c.set_editor_property("light_color", unreal.Color(255, 240, 210, 255))

    # skylight
    sk = _spawn(unreal.SkyLight.static_class(), unreal.Vector(0, 0, 300), unreal.Rotator(0, 0, 0), "SkyLight")
    if sk:
        c = _light_component(sk)
        c.set_editor_property("intensity", 1.0)

    # key rect light (specular streak)
    rl = _spawn(unreal.RectLight.static_class(), unreal.Vector(-22, 16, 26),
                _look_at(unreal.Vector(-22, 16, 26), unreal.Vector(0, 0, 8)), "KeyRect")
    if rl:
        c = _light_component(rl)
        c.set_editor_property("intensity", 10.0 * key_i)
        c.set_editor_property("source_width", 8.0)
        c.set_editor_property("source_height", 16.0)
        c.set_editor_property("attenuation_radius", 250.0)
        c.set_editor_property("light_color", unreal.Color(255, 250, 235, 255))

    # rim rect light (edge highlight)
    rr = _spawn(unreal.RectLight.static_class(), unreal.Vector(24, -18, 14),
                _look_at(unreal.Vector(24, -18, 14), unreal.Vector(0, 0, 6)), "RimRect")
    if rr:
        c = _light_component(rr)
        c.set_editor_property("intensity", 6.0 * rim_i)
        c.set_editor_property("source_width", 6.0)
        c.set_editor_property("source_height", 14.0)
        c.set_editor_property("attenuation_radius", 220.0)
        c.set_editor_property("light_color", unreal.Color(200, 220, 255, 255))


def place_post_and_camera():
    d = {k: v[0] for k, v in P.SCALARS.items()}
    expo = d.get("ExposureBias", 0.0)

    ppv = _spawn(unreal.PostProcessVolume.static_class(), unreal.Vector(0, 0, 100), unreal.Rotator(0, 0, 0), "PostProcess")
    if ppv:
        ppv.set_editor_property("unbound", True)
        try:
            settings = ppv.get_editor_property("settings")
            settings.set_editor_property("auto_exposure_bias", float(expo))
            ppv.set_editor_property("settings", settings)
        except Exception as e:
            C.log("post-process settings FAIL: " + repr(e))

    # player start (flying spectator pawn spawns here)
    _spawn(unreal.PlayerStart.static_class(), unreal.Vector(26, 26, 16),
           _look_at(unreal.Vector(26, 26, 16), unreal.Vector(0, 0, 4)), "PlayerStart")

    # cinematic camera for framing / sequencer
    cam = _spawn(unreal.CineCameraActor.static_class(), unreal.Vector(20, -28, 14),
                 _look_at(unreal.Vector(20, -28, 14), unreal.Vector(0, 0, 4)), "HeroCamera")
    if cam:
        cc = cam.get_component_by_class(unreal.CineCameraComponent)
        if cc:
            cc.set_editor_property("current_focal_length", 50.0)
            cc.set_editor_property("current_aperture", 2.8)


def run():
    C.log("=== make_level ===")
    C.ensure_dir(P.MAP_PATH)
    try:
        unreal.EditorLevelLibrary.new_level(P.LEVEL_PATH)
        C.log("new level: " + P.LEVEL_PATH)
    except Exception as e:
        C.log("new_level FAIL: " + repr(e) + " (continuing in current level)")
    place_scene()
    place_lights()
    place_post_and_camera()
    try:
        unreal.EditorLevelLibrary.save_current_level()
        C.log("saved level")
    except Exception as e:
        C.log("save_current_level FAIL: " + repr(e))
    C.log("=== make_level done ===")


if __name__ == "__main__":
    run()
