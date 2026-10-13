#include "LiquidGlassHUD.h"
#include "LiquidGlassPlayerController.h"
#include "Engine/Canvas.h"

void ALiquidGlassHUD::DrawHUD()
{
    Super::DrawHUD();

    ALiquidGlassPlayerController* PC = Cast<ALiquidGlassPlayerController>(GetOwningPlayerController());
    if (!PC) return;

    float X = 40.0f, Y = 40.0f;
    DrawText(TEXT("Liquid Glass Demo - tweak panel"), FColor::White, X, Y);
    Y += 22.0f;
    DrawText(TEXT("Tab: next | <-/-> adjust | Shift: coarse | Up/Down: coarse | R: reset | WASD+mouse: fly/orbit"),
        FColor::Cyan, X, Y);
    Y += 30.0f;

    const int32 Count = PC->GetParamCount();
    const int32 Selected = PC->GetSelectedIndex();
    for (int32 i = 0; i < Count; ++i)
    {
        FString Line = FString::Printf(TEXT("%s%s = %.3f"),
            (i == Selected) ? TEXT("> ") : TEXT("  "),
            *PC->GetParamName(i).ToString(),
            PC->GetParamValue(i));
        DrawText(Line, (i == Selected) ? FColor::Yellow : FColor::White, X, Y);
        Y += 18.0f;
    }
}
