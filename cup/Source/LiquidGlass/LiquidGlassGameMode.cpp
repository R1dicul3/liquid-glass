#include "LiquidGlassGameMode.h"
#include "LiquidGlassPlayerController.h"
#include "LiquidGlassHUD.h"
#include "GameFramework/DefaultPawn.h"

ALiquidGlassGameMode::ALiquidGlassGameMode()
{
    PlayerControllerClass = ALiquidGlassPlayerController::StaticClass();
    HUDClass = ALiquidGlassHUD::StaticClass();
    DefaultPawnClass = ADefaultPawn::StaticClass(); // flying spectator (WASD + mouse orbit)
}
