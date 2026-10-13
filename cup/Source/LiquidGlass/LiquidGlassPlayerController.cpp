#include "LiquidGlassPlayerController.h"
#include "Materials/MaterialParameterCollection.h"
#include "Materials/MaterialParameterCollectionInstance.h"
#include "EngineUtils.h"
#include "Engine/World.h"

ALiquidGlassPlayerController::ALiquidGlassPlayerController()
{
    ScalarParams = {
        TEXT("GlassIOR"), TEXT("GlassRoughness"),
        TEXT("LiquidIOR"), TEXT("LiquidRoughness"),
        TEXT("IceIOR"), TEXT("IceRoughness"),
        TEXT("KeyLightIntensity"), TEXT("RimLightIntensity"),
        TEXT("ExposureBias")
    };
}

FName ALiquidGlassPlayerController::GetParamName(int32 Index) const
{
    if (Index >= 0 && Index < ScalarParams.Num()) return ScalarParams[Index];
    return TEXT("LiquidFill");
}

float ALiquidGlassPlayerController::GetParamValue(int32 Index) const
{
    if (Index >= 0 && Index < ScalarParams.Num()) return CurrentValues.FindRef(ScalarParams[Index]);
    return LiquidFill;
}

void ALiquidGlassPlayerController::BeginPlay()
{
    Super::BeginPlay();

    ParameterCollection = LoadObject<UMaterialParameterCollection>(
        nullptr, TEXT("/Game/LiquidGlass/Params/MPC_LiquidGlass.MPC_LiquidGlass"));
    if (ParameterCollection && GetWorld())
    {
        MPCInstance = GetWorld()->GetParameterCollectionInstance(ParameterCollection);
    }

    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        if (It->GetActorLabel() == TEXT("Liquid"))
        {
            LiquidActor = *It;
            break;
        }
    }

    LoadState();
}

void ALiquidGlassPlayerController::LoadState()
{
    CurrentValues.Reset();
    DefaultValues.Reset();
    if (MPCInstance)
    {
        for (const FName& Name : ScalarParams)
        {
            float V = 0.0f;
            if (MPCInstance->GetScalarParameterValue(Name, V))
            {
                CurrentValues.Add(Name, V);
                DefaultValues.Add(Name, V);
            }
        }
    }
    LiquidFill = LiquidFillDefault;
    ApplyCurrent();
}

void ALiquidGlassPlayerController::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (WasInputKeyJustPressed(EKeys::Tab)) NextParam();
    if (WasInputKeyJustPressed(EKeys::Left)) Adjust(-0.02f, -0.15f);
    if (WasInputKeyJustPressed(EKeys::Right)) Adjust(0.02f, 0.15f);
    if (WasInputKeyJustPressed(EKeys::Down)) Adjust(-0.15f, -0.3f);
    if (WasInputKeyJustPressed(EKeys::Up)) Adjust(0.15f, 0.3f);
    if (WasInputKeyJustPressed(EKeys::R)) ResetAll();
}

void ALiquidGlassPlayerController::NextParam()
{
    CurrentParamIndex = (CurrentParamIndex + 1) % GetParamCount();
}

void ALiquidGlassPlayerController::PrevParam()
{
    CurrentParamIndex = (CurrentParamIndex + GetParamCount() - 1) % GetParamCount();
}

void ALiquidGlassPlayerController::Adjust(float Fine, float Coarse)
{
    const bool bCoarse = IsInputKeyDown(EKeys::LeftShift) || IsInputKeyDown(EKeys::RightShift);
    const float Delta = bCoarse ? Coarse : Fine;

    if (CurrentParamIndex < ScalarParams.Num())
    {
        FName Name = ScalarParams[CurrentParamIndex];
        float V = CurrentValues.FindRef(Name);
        V = FMath::Max(0.0f, V * (1.0f + Delta));
        CurrentValues.Add(Name, V);
        ApplyCurrent();
    }
    else
    {
        LiquidFill = FMath::Clamp(LiquidFill + Delta, 0.05f, 1.0f);
        if (LiquidActor)
        {
            LiquidActor->SetActorScale3D(FVector(1.0f, 1.0f, LiquidFill));
        }
    }
}

void ALiquidGlassPlayerController::ResetAll()
{
    for (const FName& Name : ScalarParams)
    {
        CurrentValues.Add(Name, DefaultValues.FindRef(Name));
    }
    LiquidFill = LiquidFillDefault;
    ApplyCurrent();
}

void ALiquidGlassPlayerController::ApplyCurrent()
{
    if (!MPCInstance) return;
    for (const FName& Name : ScalarParams)
    {
        MPCInstance->SetScalarParameterValue(Name, CurrentValues.FindRef(Name));
    }
    if (LiquidActor)
    {
        LiquidActor->SetActorScale3D(FVector(1.0f, 1.0f, LiquidFill));
    }
}
