# -*- coding: utf-8 -*-
"""Create the Material Parameter Collection (MPC) from the params.py contract."""
import unreal
import params as P
import common as C


def run():
    C.log("=== make_mpc ===")
    if C.asset_exists(P.MPC):
        C.delete_asset(P.MPC)
    C.ensure_dir(P.MPC_PATH)
    fac = unreal.MaterialParameterCollectionFactoryNew()
    mpc = C.create_asset("MPC_LiquidGlass", P.MPC_PATH, unreal.MaterialParameterCollection, fac)
    if mpc is None:
        C.log("FAILED to create MPC"); return None

    scalars = []
    for name, (default, _mn, _mx) in P.SCALARS.items():
        sp = unreal.CollectionScalarParameter()
        sp.set_editor_property("parameter_name", name)
        sp.set_editor_property("default_value", float(default))
        scalars.append(sp)

    vectors = []
    for name, (rgb, _desc) in P.VECTORS.items():
        vp = unreal.CollectionVectorParameter()
        vp.set_editor_property("parameter_name", name)
        vp.set_editor_property("default_value", unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
        vectors.append(vp)

    mpc.set_editor_property("scalar_parameters", scalars)
    mpc.set_editor_property("vector_parameters", vectors)
    C.save_asset(P.MPC)
    C.log("MPC created: %d scalars, %d vectors" % (len(scalars), len(vectors)))
    return mpc


if __name__ == "__main__":
    run()
