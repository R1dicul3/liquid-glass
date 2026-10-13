# Getting Started

## Prerequisites
- Unreal Engine **5.8.2** installed at `D:\UE_5.8` (or wherever `EngineAssociation` points).
- (C++ module only) Visual Studio 2022/2026 with the Windows C++ workload — confirmed present on this machine (MSVC 14.51 + Win SDK 10.0.26100).
- Python is bundled with the editor; no separate Python needed.

## 1. Build the scene (one-time / anytime)
From a terminal:

```
"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "D:\ue5\liquied\cup\cup.uproject" ^
  -run=pythonscript -script="D:\ue5\liquied\scripts\bootstrap.py" -stdout -unattended -nosplash
```

This (idempotently) rebuilds, in order:
1. `MPC_LiquidGlass` — the parameter collection (all tweakables).
2. `SM_Tumbler`, `SM_Liquid` — procedural lathe meshes (OBJ -> import).
3. `M_Glass / M_Liquid / M_Ice / M_Stone / M_Table / M_Backdrop` — Substrate materials.
4. `LiquidGlassDemo` — the level (actors + lights + camera + post-process).

The log is written to `outputs/build_log.txt`.

> You can also run individual modules in the editor Output Log (Console):
> `py scripts/make_meshes.py`, `py scripts/make_materials.py`, etc. — decoupled by design.

## 2. Open and play
1. Open `cup/cup.uproject` in Unreal Editor 5.8.
2. First open compiles shaders (Substrate + SM6 + Lumen + RayTracing) — give it a few minutes.
3. Open `/Game/LiquidGlass/Maps/LiquidGlassDemo`.
4. Press **Play (Alt+P)**. You spawn at the PlayerStart as a flying spectator pawn:
   - **WASD** move, **mouse** look, **Q/E** down/up (spectator defaults).
   - Fly around the glass to inspect refraction/reflection from every angle.

## 3. Tweak by eye
See [TUNING_GUIDE.md](TUNING_GUIDE.md). Short version:
- Edit `configs/tuning.json` then run `py scripts/tune.py` in the editor Output Log (applies live).
- Or open `MPC_LiquidGlass` and drag the scalar/vector values directly.
- The C++ in-game panel (if built) lets you adjust with keys during Play.

## 4. Repo
```
git clone https://github.com/R1dicul3/liquid-glass.git
```
`Intermediate/`, `Saved/`, `DerivedDataCache/`, `Binaries/` and `outputs/` are git-ignored;
`Config/` and `Content/` (generated assets) are committed.
