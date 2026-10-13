# -*- coding: utf-8 -*-
"""Procedural mesh generation: lathe (surface-of-revolution) -> OBJ -> imported StaticMesh.

The geometry is generated analytically in Python (vertices/UVs/normals/triangles),
written to a temporary .obj, and imported so the engine computes tangents and
builds render data. Only the hero geometry (glass tumbler + liquid volume) lives
here; secondary meshes reuse engine basic shapes in make_level.py.

Units: cm. Z is up.
"""
import math
import os
import unreal
import params as P
import common as C

MESH_CACHE = r"D:\ue5\liquied\outputs\mesh_cache"


def _revolve(profile, segments, flip=False):
    """Revolve profile [(r,z)] (bottom->top) around Z. Returns (verts, uvs, norms, tris)."""
    n = len(profile)
    verts, uvs, norms, tris = [], [], [], []
    for s in range(segments):
        t = 2.0 * math.pi * s / segments
        c, sn = math.cos(t), math.sin(t)
        for j in range(n):
            r, z = profile[j]
            verts.append((r * c, r * sn, z))
            uvs.append((s / float(segments), j / float(max(1, n - 1))))
            jm = max(0, j - 1); jp = min(n - 1, j + 1)
            dr = profile[jp][0] - profile[jm][0]
            dz = profile[jp][1] - profile[jm][1]
            nx, ny, nz = dz * c, dz * sn, -dr
            L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            if flip:
                nx, ny, nz = -nx, -ny, -nz
            norms.append((nx / L, ny / L, nz / L))
    for s in range(segments):
        s1 = (s + 1) % segments
        for j in range(n - 1):
            a = s * n + j; b = s1 * n + j; c = s1 * n + j + 1; d = s * n + j + 1
            if not flip:
                tris.append((a, b, c)); tris.append((a, c, d))
            else:
                tris.append((a, c, b)); tris.append((a, d, c))
    return verts, uvs, norms, tris


def _disc(z, r0, r1, segments, facing_up=True):
    """Flat annulus (r0..r1, r0 may be 0) at height z. Returns (verts, uvs, norms, tris)."""
    verts, uvs, norms, tris = [], [], [], []
    nz = 1.0 if facing_up else -1.0
    for s in range(segments):
        t = 2.0 * math.pi * s / segments
        c, sn = math.cos(t), math.sin(t)
        verts.append((r0 * c, r0 * sn, z)); uvs.append((0.0, 0.0)); norms.append((0.0, 0.0, nz))
    for s in range(segments):
        t = 2.0 * math.pi * s / segments
        c, sn = math.cos(t), math.sin(t)
        verts.append((r1 * c, r1 * sn, z)); uvs.append((1.0, 1.0)); norms.append((0.0, 0.0, nz))
    for s in range(segments):
        s1 = (s + 1) % segments
        i0, i1, o0, o1 = s, s1, segments + s, segments + s1
        if facing_up:
            tris.append((i0, o0, o1)); tris.append((i0, o1, i1))
        else:
            tris.append((i0, o1, o0)); tris.append((i0, i1, o1))
    return verts, uvs, norms, tris


def _merge(*parts):
    verts, uvs, norms, tris = [], [], [], []
    for (v, u, n, t) in parts:
        off = len(verts)
        verts.extend(v); uvs.extend(u); norms.extend(n)
        tris.extend((a + off, b + off, c + off) for (a, b, c) in t)
    return verts, uvs, norms, tris


def _write_obj(path, verts, uvs, norms, tris):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["# liquid-glass procedural mesh"]
    for (x, y, z) in verts:
        lines.append("v %.6f %.6f %.6f" % (x, y, z))
    for (u, v) in uvs:
        lines.append("vt %.6f %.6f" % (u, v))
    for (nx, ny, nz) in norms:
        lines.append("vn %.6f %.6f %.6f" % (nx, ny, nz))
    for (a, b, c) in tris:
        lines.append("f %d/%d/%d %d/%d/%d %d/%d/%d" % (a + 1, a + 1, a + 1, b + 1, b + 1, b + 1, c + 1, c + 1, c + 1))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def build_static_mesh(asset_path, verts, uvs, norms, tris):
    name = asset_path.rsplit("/", 1)[1]
    pkg = asset_path.rsplit("/", 1)[0]
    if C.asset_exists(asset_path):
        C.delete_asset(asset_path)
    C.ensure_dir(pkg)
    obj_path = _write_obj(os.path.join(MESH_CACHE, name + ".obj"), verts, uvs, norms, tris)
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", obj_path)
    task.set_editor_property("destination_path", pkg)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    task.set_editor_property("replace_existing", True)
    at = unreal.AssetToolsHelpers.get_asset_tools()
    at.import_asset_tasks([task])
    sm = C.load_asset(asset_path)
    if sm is None:
        C.log("FAILED import " + asset_path); return None
    C.log("Built " + asset_path + " (%d verts, %d tris)" % (len(verts), len(tris)))
    return sm


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------
def _rounded_outer(tb, n=7):
    R_bot, R_top, H, bevel = tb["radius_bottom"], tb["radius_top"], tb["height"], tb["bevel"]
    prof = []
    for i in range(n):
        a = (math.pi / 2.0) * i / (n - 1)
        prof.append((R_bot - bevel + bevel * math.sin(a), bevel * (1.0 - math.cos(a))))
    prof.append((R_top, H))
    return prof


def _rounded_inner(tb, n=7):
    R_bot, R_top, H, wall, base, bevel = (tb["radius_bottom"], tb["radius_top"], tb["height"],
                                          tb["wall"], tb["base"], tb["bevel"])
    r_in = R_bot - wall
    prof = []
    for i in range(n):
        a = (math.pi / 2.0) * i / (n - 1)
        prof.append((r_in - bevel + bevel * math.sin(a), base + bevel * (1.0 - math.cos(a))))
    prof.append((R_top - wall, H - wall))
    return prof


def make_tumbler():
    tb = P.TUMBLER
    seg = tb["segments"]
    R_bot, R_top, H, wall, base, bevel = (tb["radius_bottom"], tb["radius_top"], tb["height"],
                                          tb["wall"], tb["base"], tb["bevel"])
    outer_wall = _revolve(_rounded_outer(tb), seg, flip=False)
    inner_wall = _revolve(_rounded_inner(tb), seg, flip=True)
    bottom = _disc(0.0, 0.0, R_bot - bevel, seg, facing_up=False)
    inner_bottom = _disc(base, 0.0, (R_bot - wall) - bevel, seg, facing_up=True)
    rim = _disc(H, R_top - wall, R_top, seg, facing_up=True)
    v, u, n, t = _merge(outer_wall, inner_wall, bottom, inner_bottom, rim)
    return build_static_mesh(P.SM_TUMBLER, v, u, n, t)


def make_liquid():
    tb = P.TUMBLER
    liq = P.LIQUID
    seg = tb["segments"]
    R_bot, R_top, H, wall, base = (tb["radius_bottom"], tb["radius_top"], tb["height"],
                                   tb["wall"], tb["base"])
    r_bot = (R_bot - wall) - liq["inset"]
    r_top = (R_top - wall) - liq["inset"]
    inner_h = (H - wall) - base   # full liquid height, authored from local z=0 (pivot at base)
    profile = [(r_bot, 0.0), (r_top, inner_h)]
    side = _revolve(profile, seg, flip=False)
    top_disc = _disc(inner_h, 0.0, r_top, seg, facing_up=True)
    bot_disc = _disc(0.0, 0.0, r_bot, seg, facing_up=False)
    v, u, n, t = _merge(side, top_disc, bot_disc)
    return build_static_mesh(P.SM_LIQUID, v, u, n, t)


def run():
    C.log("=== make_meshes ===")
    make_tumbler()
    make_liquid()
    C.log("=== make_meshes done ===")


if __name__ == "__main__":
    run()
