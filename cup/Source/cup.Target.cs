using UnrealBuildTool;
using System.Collections.Generic;

public class cupTarget : TargetRules
{
    public cupTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("LiquidGlass");
    }
}
