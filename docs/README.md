# liquid-glass — 杯中液体渲染 (Liquid-in-Glass Rendering)

A real-time **glass + liquid rendering showcase** built in Unreal Engine 5.8 for a
Technical-Artist portfolio. Focus areas: physically-based **glass reflection/refraction**,
**liquid transparency & volumetric absorption**, an **object submerged in the liquid**,
and a **live tweak surface** to adjust every physical/rendering parameter by hand.

> Live repo: https://github.com/R1dicul3/liquid-glass (public)

## What it demonstrates (TA showcase points)
- **Substrate (Strata) materials** — slab BSDF transmission for glass, ice and liquid.
- **Lumen + Hardware Ray Tracing** — reflections, refractions, soft shadows, GI.
- **Beer–Lambert absorption** in the liquid (colour deepens with thickness).
- **Procedural geometry** — the glass tumbler and the liquid volume are generated
  by a Python *surface-of-revolution (lathe)* pipeline, not hand-authored meshes.
- **A decoupled, scriptable content pipeline** — every asset is rebuilt from Python,
  so the whole scene is reproducible and debuggable in isolation.
- **A tweak surface** — one Material Parameter Collection drives every physical
  parameter; an editor script + a C++ in-game panel let you tune by eye.

## Tech stack
| Layer | Choice |
|---|---|
| Engine | Unreal Engine **5.8.2** (SM6, DX12) |
| Materials | **Substrate** slab BSDF (transmission) |
| GI / reflections | **Lumen** + Hardware Ray Tracing |
| Content pipeline | **Unreal Python** (`-run=pythonscript`) |
| Interaction | **C++** actor module (drag-to-orbit + live tweak keys) |
| Parameter contract | **Material Parameter Collection (MPC)** |

## Repository layout
```
cup/            UE project (cup.uproject, Config/, Content/)
scripts/        Decoupled Python build pipeline (see docs/ARCHITECTURE.md)
  params.py       single source of truth: asset paths + parameter contract
  common.py       logging + idempotent asset find/create/save helpers
  make_meshes.py  procedural lathe -> glass tumbler + liquid volume
  make_mpc.py     material parameter collection
  make_materials.py  Substrate glass / liquid / ice / stone / table
  make_level.py   level assembly: actors, lights, camera, post-process
  tune.py         apply configs/tuning.json -> MPC (live, editor)
  bootstrap.py    run everything end-to-end
configs/tuning.json   the tunable parameter values
docs/           README / ARCHITECTURE / TUNING_GUIDE / DECISIONS
Source/         C++ module (interaction + runtime tweak panel)
```

## Quick start
1. Open `cup/cup.uproject` in Unreal Editor 5.8.
2. (First time) run the build pipeline once:
   ```
   "D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "cup\cup.uproject" ^
     -run=pythonscript -script="scripts\bootstrap.py" -stdout -unattended -nosplash
   ```
   (or open the Output Log and run `py scripts/bootstrap.py`).
3. Open `/Game/LiquidGlass/Maps/LiquidGlassDemo`.
4. Play (PIE) and drag the mouse to orbit the glass; use the tweak keys (see
   docs/TUNING_GUIDE.md) to adjust IOR, absorption, fill level, etc. live.

See docs/GETTING_STARTED.md and docs/TUNING_GUIDE.md for full details.
