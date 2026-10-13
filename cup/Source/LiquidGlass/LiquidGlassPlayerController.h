#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "LiquidGlassPlayerController.generated.h"

class UMaterialParameterCollection;
class UMaterialParameterCollectionInstance;

UCLASS()
class LIQUIDGLASS_API ALiquidGlassPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    ALiquidGlassPlayerController();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    // readable by the HUD
    int32  GetParamCount() const { return ScalarParams.Num() + 1; }
    FName  GetParamName(int32 Index) const;
    float  GetParamValue(int32 Index) const;
    int32  GetSelectedIndex() const { return CurrentParamIndex; }

protected:
    UPROPERTY() TObjectPtr<UMaterialParameterCollection> ParameterCollection;
    UPROPERTY() TObjectPtr<UMaterialParameterCollectionInstance> MPCInstance;
    UPROPERTY() TObjectPtr<AActor> LiquidActor;

    TArray<FName> ScalarParams;
    TMap<FName, float> CurrentValues;
    TMap<FName, float> DefaultValues;
    int32 CurrentParamIndex = 0;
    float LiquidFill = 0.60f;
    float LiquidFillDefault = 0.60f;

    void NextParam();
    void PrevParam();
    void Adjust(float Fine, float Coarse);
    void ResetAll();
    void ApplyCurrent();
    void LoadState();
};
