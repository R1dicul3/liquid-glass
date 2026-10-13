# -*- coding: utf-8 -*-
"""Procedural mesh generation.

Lathe (surface-of-revolution) meshes -> StaticMesh assets. Only the hero
geometry (glass tumbler + liquid volume) is generated here; secondary meshes
(ice cube, stone, table, backdrop) reuse engine basic shapes in make_level.py.

Units: Unreal Units == cm. Z is up.
"""
import math
import unreal
import params as P
import common as C


# ---------------------------------------------------------------------------
# Geometry primitives (pure math -> lists)
# ---------------------------------------------------------------------------
def _revolve(profile, segments, flip=False):
    """Revolve a profile [(r, z), ...] (bottom->top) around the Z axis.

    Returns (verts, uvs, tris). flip=False gives outward-facing (+radial) winding.
    """
    n = len(profile)
    verts, uvs, tris = [], [], []
    for s in range(segments):
        t = 2.0 * math.pi * s / segments
        c, sn = math.cos(t), math.sin(t)
        for j in range(n):
            r, z = profile[j]
            verts.append((r * c, r * sn, z))
            uvs.append((s / float(segments), j / float(max(1, n - 1))))
    for s in range(segments):
        s1 = (s + 1) % segments
        for j in range(n - 1):
            a = s * n + j
            b = s1 * n + j
            c = s1 * n + j + 1
            d = s * n + j + 1
            if not flip:
                tris.append((a, b, c)); tris.append((a, c, d))
            else:
                tris.append((a, c, b)); tris.append((a, d, c))
    return verts, uvs, tris


def _disc(z, r0, r1, segments, facing_up=True):
    """Flat annulus (r0..r1, r0 may be 0) at height z. Normal +Z if facing_up."""
    verts, uvs, tris = [], [], []
    for s in range(segments):
        t = 2.0 * math.pi * s / segments
        c, sn = math.cos(t), math.sin(t)
        verts.append((r0 * c, r0 * sn, z)); uvs.append((0.0, 0.0))
    for s in range(segments):
        t = 2.0 * math.pi * s / segments
        c, sn = math.cos(t), math.sin(t)
        verts.append((r1 * c, r1 * sn, z)); uvs.append((1.0, 1.0))
    for s in range(segments):
        s1 = (s + 1) % segments
        i0, i1, o0, o1 = s, s1, segments + s, segments + s1
        if facing_up:
            tris.append((i0, o0, o1)); tris.append((i0, o1, i1))
        else:
            tris.append((i0, o1, o0)); tris.append((i0, i1, o1))
    return verts, uvs, tris


def _merge(*parts):
    """Merge several (verts, uvs, tris) with index offsets."""
    verts, uvs, tris = [], [], []
    for (v, u, t) in parts:
        off = len(verts)
        verts.extend(v); uvs.extend(u)
        tris.extend((a + off, b + off, c + off) for (a, b, c) in t)
    return verts, uvs, tris


# ---------------------------------------------------------------------------
# StaticMesh asset builder
# ---------------------------------------------------------------------------
def build_static_mesh(asset_path, verts, uvs, tris):
    name = asset_path.rsplit("/", 1)[1]
    pkg = asset_path.rsplit("/", 1)[0]
    if C.asset_exists(asset_path):
        C.delete_asset(asset_path)
    C.ensure_dir(pkg)
    at = unreal.AssetToolsHelpers.get_asset_tools()
    sm = at.create_asset(name, pkg, unreal.StaticMesh, unreal.StaticMeshFactory())
    if sm is None:
        C.log("FAILED create " + asset_path)
        return None

    md = unreal.StaticMeshDescription()
    V, T = len(verts), len(tris)
    md.reserve_new_vertices(V)
    md.reserve_new_vertex_instances(V)
    md.reserve_new_triangles(T)
    md.reserve_new_polygon_groups(1)
    pg = md.create_polygon_group()

    for i, (x, y, z) in enumerate(verts):
        md.set_vertex_position(i, unreal.Vector(x, y, z))
    for i in range(V):
        vi = md.create_vertex_instance(i)
        md.set_vertex_instance_uv(vi, unreal.Vector2D(uvs[i][0], uvs[i][1]), 0)
    for (a, b, c) in tris:
        md.create_triangle(pg, [a, b, c])
    md.compute_polygon_tangents_and_normals([pg])

    method = "none"
    try:
        if hasattr(sm, "build_from_mesh_descriptions"):
            sm.build_from_mesh_descriptions([md]); method = "build_from_mesh_descriptions"
        elif hasattr(sm, "build_from_mesh_description"):
            sm.build_from_mesh_description(md); method = "build_from_mesh_description"
        else:
            C.log("NO build_from_mesh method found on StaticMesh"); return None
    except Exception as e:
        C.log("build_from_mesh FAILED (" + method + "): " + repr(e)); return None

    C.save_asset(asset_path)
    C.log("Built " + asset_path + " (%d verts, %d tris, " % (V, T) + method + ")")
    return sm


# ---------------------------------------------------------------------------
# Glass tumbler (closed, thick-walled shell)
# ---------------------------------------------------------------------------
def _rounded_outer(tb, n=6):
    """Outer wall profile bottom->top with a rounded bottom corner."""
    R_bot, R_top, H, bevel = tb["radius_bottom"], tb["radius_top"], tb["height"], tb["bevel"]
    prof = []
    for i in range(n):
        a = (math.pi / 2.0) * i / (n - 1)
        prof.append((R_bot - bevel + bevel * math.sin(a), bevel * (1.0 - math.cos(a))))
    prof.append((R_top, H))
    return prof


def _rounded_inner(tb, n=6):
    """Inner wall profile bottom->top (inside the cavity)."""
    R_bot, R_top, H, wall, base, bevel = (tb["radius_bottom"], tb["radius_top"],
                                          tb["height"], tb["wall"], tb["base"], tb["bevel"])
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
    inner_wall = _revolve(_rounded_inner(tb), seg, flip=True)      # inward-facing
    bottom = _disc(0.0, 0.0, R_bot - bevel, seg, facing_up=False)  # base underside
    inner_bottom = _disc(base, 0.0, (R_bot - wall) - bevel, seg, facing_up=True)
    rim = _disc(H, R_top - wall, R_top, seg, facing_up=True)
    v, u, t = _merge(outer_wall, inner_wall, bottom, inner_bottom, rim)
    return build_static_mesh(P.SM_TUMBLER, v, u, t)


# ---------------------------------------------------------------------------
# Liquid volume (closed, sits inside the cavity; authored full-height)
# ---------------------------------------------------------------------------
def make_liquid():
    tb = P.TUMBLER
    liq = P.LIQUID
    seg = tb["segments"]
    R_bot, R_top, H, wall, base = (tb["radius_bottom"], tb["radius_top"], tb["height"],
                                   tb["wall"], tb["base"])
    r_bot = (R_bot - wall) - liq["inset"]
    r_top = (R_top - wall) - liq["inset"]
    top = H - wall  # full inner height (scaled later by actor Z-scale = fill)
    profile = [(r_bot, base), (r_top, top)]
    side = _revolve(profile, seg, flip=False)
    top_disc = _disc(top, 0.0, r_top, seg, facing_up=True)
    bot_disc = _disc(base, 0.0, r_bot, seg, facing_up=False)
    v, u, t = _merge(side, top_disc, bot_disc)
    return build_static_mesh(P.SM_LIQUID, v, u, t)


def run():
    C.log("=== make_meshes ===")
    make_tumbler()
    make_liquid()
    C.log("=== make_meshes done ===")


if __name__ == "__main__":
    run()
