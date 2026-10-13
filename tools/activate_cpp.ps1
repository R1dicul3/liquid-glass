# tools/activate_cpp.ps1
# Activate + build the C++ interaction/tweak module.
# PREREQUISITE: close Unreal Editor first (Live Coding blocks UBT builds).
param([string]$Project = "D:\ue5\liquied\cup\cup.uproject")

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path $Project

$procs = Get-Process -Name "UnrealEditor","UnrealEditor-Cmd","LiveCodingConsole" -ErrorAction SilentlyContinue
if ($procs) {
    Write-Host "ERROR: close Unreal Editor first (running: $($procs.ProcessName -join ', '))" -ForegroundColor Red
    exit 1
}

# 1. write the C++ .uproject (adds the LiquidGlass runtime module)
@'
{
	"FileVersion": 3,
	"EngineAssociation": "5.8",
	"Category": "",
	"Description": "Liquid-in-glass rendering showcase (Substrate + Lumen + RayTracing)",
	"Modules": [
		{
			"Name": "LiquidGlass",
			"Type": "Runtime",
			"LoadingPhase": "Default"
		}
	],
	"Plugins": [
		{
			"Name": "ModelingToolsEditorMode",
			"Enabled": true,
			"TargetAllowList": [ "Editor" ]
		},
		{
			"Name": "PythonScriptPlugin",
			"Enabled": true,
			"TargetAllowList": [ "Editor" ]
		},
		{
			"Name": "EditorScriptingUtilities",
			"Enabled": true,
			"TargetAllowList": [ "Editor" ]
		}
	]
}
'@ | Set-Content -Encoding UTF8 (Join-Path $ProjectDir "cup.uproject")

# 2. set the C++ game mode + default map
@'

[/Script/CommonUI.CommonUISettings]
CommonButtonAcceptKeyHandling=TriggerClick

[ConsoleVariables]
CommonUI.CheckKeyboardFocusAndParentage=1
CommonUI.DisallowUserFocusedWidgetForPendingFocusRecipient=1
CommonUI.FallbackToDesiredOnAutoRestoreFailure=1

[/Script/EngineSettings.GeneralProjectSettings]
ProjectID=4E9873AC45311144E60AD796BF2850B5

[/Script/EngineSettings.GameMapsSettings]
GlobalDefaultGameMode=/Script/LiquidGlass.LiquidGlassGameMode
GameDefaultMap=/Game/LiquidGlass/Maps/LiquidGlassDemo
'@ | Set-Content -Encoding UTF8 (Join-Path $ProjectDir "Config\DefaultGame.ini")

# 3. build
& "D:\UE_5.8\Engine\Build\BatchFiles\Build.bat" cupEditor Win64 Development -project="$Project" -waitmutex
if ($LASTEXITCODE -ne 0) { Write-Host "BUILD FAILED" -ForegroundColor Red; exit 1 }
Write-Host "C++ module built. Reopen the editor and Play (Alt+P): drag mouse to orbit, Tab/arrows to tweak." -ForegroundColor Green
