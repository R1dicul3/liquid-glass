# -*- coding: utf-8 -*-
"""Entry point: rebuild the whole scene end-to-end (decoupled, idempotent)."""
import sys, os
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.abspath(".")
sys.path.insert(0, _SCRIPT_DIR)

import common as C
import make_mpc
import make_meshes
import make_materials
import make_level


def main():
    C.log("=========== BOOTSTRAP START ===========")
    try:
        make_mpc.run()
    except Exception as e:
        C.log("make_mpc ERROR: " + repr(e))
    try:
        make_meshes.run()
    except Exception as e:
        C.log("make_meshes ERROR: " + repr(e))
    try:
        make_materials.run()
    except Exception as e:
        C.log("make_materials ERROR: " + repr(e))
    try:
        make_level.run()
    except Exception as e:
        C.log("make_level ERROR: " + repr(e))
    C.log("=========== BOOTSTRAP DONE ===========")


if __name__ == "__main__":
    main()
