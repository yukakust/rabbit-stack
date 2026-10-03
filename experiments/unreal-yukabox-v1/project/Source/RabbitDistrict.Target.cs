using UnrealBuildTool;
using System.Collections.Generic;

public class RabbitDistrictTarget : TargetRules
{
    public RabbitDistrictTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("RabbitDistrict");
    }
}
