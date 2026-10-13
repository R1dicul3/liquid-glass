#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "LiquidGlassHUD.generated.h"

UCLASS()
class LIQUIDGLASS_API ALiquidGlassHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};
