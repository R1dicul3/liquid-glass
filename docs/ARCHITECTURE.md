# Architecture — module decoupling

Everything is built from **text-first, idempotent, independently runnable modules** so a
single asset can be debugged and regenerated without touching anything else.

## Principle: one parameter contract
`scripts/params.py` is the *single source of truth*. It defines:
- asset paths (`/Game/LiquidGlass/...`),
- geometry constants (`TUMBLER`, `LIQUID`),
- the tweakable parameter contract (`SCALARS`, `VECTORS`).

Every other module imports from `params.py`. The MPC (built by `make_mpc.py`) is the
*runtime* mirror of that contract: materials read the MPC, the tweak surface writes the
MPC. Change a parameter once in `params.py` and regenerate.

## Module map
```
params.py   (contract)
    |
    +--> make_mpc.py        creates MPC_LiquidGlass from SCALARS/VECTORS
    +--> make_materials.py  creates M_Glass, M_Liquid, M_Ice, ... reading MPC
    +--> make_meshes.py     creates SM_Tumbler, SM_Liquid (procedural lathe)
    +--> make_level.py      assembles actors + lights + camera + post-process
    +--> tune.py            applies configs/tuning.json -> MPC (runtime tweak)
    +--> make_tweak_ui.py   (C++ side) in-game parameter panel
bootstrap.py
    runs: make_mpc -> make_meshes -> make_materials -> make_level
```

## Data flow for a tweak
```
tuning.json  --tune.py-->  MPC_LiquidGlass  --CollectionParameter-->  Material
                                                              graph (Substrate)
C++ tweak keys (PIE)  ----------------------------------------->  MPC
```

## Idempotency
Every `make_*.py` deletes and recreates only the assets it owns, and only saves what
changed. Re-running `bootstrap.py` is safe at any time.

## Why decoupled?
- **Debug one thing at a time** — `make_meshes.py` can be run alone to inspect the
  tumbler without rebuilding materials.
- **Fast iteration** — material graph edits never touch geometry or level layout.
- **Reproducible** — a fresh clone + one command rebuilds the whole scene.
