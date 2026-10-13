# Tuning Guide — tweak the liquid & glass by eye

All physical/rendering parameters live in **one** place:
`MPC_LiquidGlass` (Material Parameter Collection), defined in `scripts/params.py`
and mirrored in `configs/tuning.json`. Materials read the MPC live.

## Three ways to tweak
1. **JSON (script)** — edit `configs/tuning.json`, then in the editor Output Log run
   `py scripts/tune.py`. Applies MPC params, liquid fill, light intensity and exposure live.
2. **MPC panel (GUI)** — open `/Game/LiquidGlass/Params/MPC_LiquidGlass`; the editor shows
   scalar sliders and colour pickers. Change a value -> materials update immediately.
3. **In-game keys (C++)** — during Play, keys cycle/adjust a curated subset (see below).

## Parameter reference
| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `GlassIOR` | scalar | 1.50 | refractive index of the glass (drives F0) |
| `GlassRoughness` | scalar | 0.02 | micro-roughness of the glass surface |
| `GlassTint` | vector | (1,1,1) | glass body tint (multiplied by 0.02 -> near-black for clear) |
| `LiquidIOR` | scalar | 1.33 | refractive index of the liquid (water ~1.33) |
| `LiquidRoughness` | scalar | 0.04 | liquid surface roughness |
| `LiquidColor` | vector | (0.52,0.30,0.11) | liquid diffuse albedo (amber/whisky) |
| `LiquidMFP` | vector | (2.0,1.0,0.45) | **mean free path (cm)** — short channel = absorbed fast |
| `IceIOR` | scalar | 1.31 | refractive index of ice |
| `IceRoughness` | scalar | 0.06 | ice roughness |
| `IceColor` | vector | (0.88,0.94,1.0) | ice diffuse albedo |
| `TableColor` | vector | (0.17,0.15,0.13) | table base colour |
| `BackdropColor` | vector | (0.52,0.56,0.62) | backdrop base colour |
| `KeyLightIntensity` | scalar | 1.0 | key light multiplier |
| `RimLightIntensity` | scalar | 1.0 | rim light multiplier |
| `ExposureBias` | scalar | 0.0 | post-process EV bias |
| `LiquidFill` | actor | 0.60 | liquid fill fraction (0..1) |

## Physical notes
- **IOR -> F0**: the Substrate slab has no IOR pin; F0 = ((IOR-1)/(IOR+1))^2 is computed
  in-graph, so tweaking `GlassIOR`/etc. maps directly to the Schlick reflectance.
- **Absorption (Beer–Lambert)**: `LiquidMFP` is the per-channel mean free path fed into
  the slab's `SSS MFP`. Short MFP = that colour is absorbed over a short distance. The
  default (2.0, 1.0, 0.45) absorbs blue fastest -> amber. Try (0.4, 0.4, 0.4) for a dense
  "juice", or (6,6,6) for near-clear water.

## Recipe ideas
- **Clear water**: `LiquidColor=(0.05,0.08,0.12)`, `LiquidMFP=(8,8,8)`, `LiquidIOR=1.33`.
- **Whisky (amber)**: `LiquidColor=(0.52,0.30,0.11)`, `LiquidMFP=(2.0,1.0,0.45)`.
- **Blue soda**: `LiquidColor=(0.05,0.20,0.45)`, `LiquidMFP=(1.5,2.5,5.0)` (blue passes deepest).
- **Frosted glass**: `GlassRoughness=0.25`, `GlassTint=(1,1,1)` (raise the 0.02 factor in make_materials.py).
