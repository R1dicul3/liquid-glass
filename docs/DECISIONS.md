# Decisions & open items for the owner

This file records what I decided (and why), what I could *not* do from this side, and
what **you** need to do / decide. Read this last.

## 1. Decisions I made (can be changed)
| Topic | Decision | Why |
|---|---|---|
| Repo | new public repo `R1dicul3/liquid-glass` | you allowed public hosting |
| Engine | UE 5.8.2 (your installed `D:\UE_5.8`) | already installed + SM6/Substrate/Lumen ready |
| Material model | **Substrate slab BSDF** (not legacy translucent) | physically-correct transmission/absorption, the modern TA story |
| Hero geometry | glass **tumbler (rocks glass)** + liquid volume, procedural lathe | shows refraction through thick walls + deep liquid; reliable |
| Secondary meshes | engine basic shapes (cube=ice, sphere=stone, slab=table) | token-cheap, zero-risk, reads clearly |
| Units | Unreal Units = cm (glass ≈ 8.7 cm tall) | physical plausibility |
| Interaction | C++ drag-to-orbit + tweak keys (VS2026 toolchain confirmed) | proper decoupled module, no hand-authored Blueprint graphs |
| Tweak surface | MPC + `tune.py` (JSON) + C++ in-game panel | Remote-Control *Python* API is absent in 5.8 |

## 2. What I could NOT do (and why)
- **Remote Control web UI via Python** — `unreal.RemoteControl*` is not exposed to
  Python in 5.8.2. Fallback: `tune.py` + MPC editor panel + C++ in-game keys.
- **MikuMikuDance assets** — `D:\mmd` does not exist; the actual folder is
  `D:\mikumikudance\character` (PMX models). I did **not** use them: a liquid demo
  needs a glass + liquid + small object, which procedural meshes cover more cleanly.
  (Optional: you may later drop a PMX character *outside* the glass as context.)
- **True meniscus / fluid simulation** — the liquid is a static volume (scaled for fill
  level). Real fluid sim (Niagara FLIP / FluX) is a separate scope; noted as future work.
- **Caustics** — Lumen gives reflected/refracted light but not sharp volumetric caustics;
  that needs the *path tracer* (movie render) or a caustics plug-in. Noted as future work.

## 3. What YOU need to do / decide
1. **Open the editor once** and let it compile shaders (Substrate+SM6+Lumen first build
   can take several minutes). Then press Play to verify the look.
2. **Pick the final "hero" look** — amber whisky vs clear water vs tinted soda. Edit
   `configs/tuning.json` `LiquidColor` / `LiquidAbsorption` (see TUNING_GUIDE).
3. **Repo metadata (optional)** — add a license, a nicer `README` banner, a
   `description` (already set to a one-liner). GitHub: Settings → general.
4. **Portfolio capture** — record a screen capture (OBS / Movie Render Queue path-trace
   stills) once the look is dialled in.
5. **Decide glass style** — currently a tumbler; the lathe pipeline can emit a wine glass
   or martini profile by editing `make_meshes.py` `_rounded_outer/_rounded_inner`.

## 4. Open questions (non-blocking)
- Do you want a **wine glass** instead of / in addition to the tumbler?
- Do you want the **ice cube** to *float* (buoyancy) or rest at the bottom? (currently
  authored resting near the bottom + one floating stone sphere)
