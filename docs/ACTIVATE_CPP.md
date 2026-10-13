# Activate the C++ interaction module (opt-in)

The demo works out-of-the-box as a **Blueprint-only** project:
- open `cup/cup.uproject` -> Play -> fly around with WASD+mouse (built-in spectator pawn)
- tweak parameters with `py scripts/tune.py` or the MPC panel (see TUNING_GUIDE.md)

A **C++ module** is also written (`cup/Source/LiquidGlass/`) that adds:
- an in-game **tweak panel** (Tab to cycle, arrows to adjust, R to reset, HUD menu)
- the flying-orbit camera wired through a custom GameMode/PlayerController/HUD.

It is **not activated yet** because Unreal Build Tool refuses to compile while
Live Coding is active (i.e. while the editor is open).

## To activate
1. Close Unreal Editor completely.
2. Run, from the repo root:
   ```
   powershell -ExecutionPolicy Bypass -File tools\activate_cpp.ps1
   ```
   (this writes the C++ `.uproject` + game-mode config, then runs UBT)
3. Reopen the editor (first open compiles the module + shaders).

To go back to Blueprint-only, restore `cup/cup.uproject` (remove the `Modules` block)
and `cup/Config/DefaultGame.ini` (remove the `GameMapsSettings` section).

The C++ sources are intentionally decoupled (GameMode / PlayerController / HUD), so you
can extend the tweak list in `LiquidGlassPlayerController.cpp` (`ScalarParams`) without
touching the render pipeline.
