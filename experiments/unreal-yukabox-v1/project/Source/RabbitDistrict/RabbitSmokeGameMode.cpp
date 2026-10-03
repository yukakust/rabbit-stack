#include "RabbitSmokeGameMode.h"
#include "Camera/CameraActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"

ARabbitSmokeGameMode::ARabbitSmokeGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
}

void ARabbitSmokeGameMode::StartPlay()
{
    Super::StartPlay();
    StartTime = FPlatformTime::Seconds();
    FParse::Value(FCommandLine::Get(), TEXT("RabbitFrame="), FramePath);
    auto Cube = [this](FVector Position, FVector Scale)
    {
        auto* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(Position, FRotator::ZeroRotator);
        auto* Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
        if (!Actor || !Mesh) return;
        Actor->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
        Actor->GetStaticMeshComponent()->SetStaticMesh(Mesh);
        Actor->SetActorScale3D(Scale);
    };
    Cube(FVector(0, 0, -25), FVector(35, 35, 0.5));
    Cube(FVector(300, -400, 200), FVector(4, 4, 4));
    Cube(FVector(700, 400, 300), FVector(4, 4, 6));
    Cube(FVector(1200, -350, 150), FVector(3, 3, 3));
    auto* Sun = GetWorld()->SpawnActor<ADirectionalLight>(FVector(0, 0, 1200), FRotator(-45, -35, 0));
    if (Sun) Sun->GetLightComponent()->SetIntensity(5.0f);
    const FVector Eye(-1100, -1500, 1100);
    const FVector LookAt(400, 0, 180);
    auto* Camera = GetWorld()->SpawnActor<ACameraActor>(Eye, (LookAt-Eye).Rotation());
    if (auto* PC = GetWorld()->GetFirstPlayerController())
        if (Camera) PC->SetViewTarget(Camera);
    UE_LOG(LogTemp, Display, TEXT("RABBIT_SMOKE_SCENE_STARTED"));
}

void ARabbitSmokeGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    const double Elapsed = FPlatformTime::Seconds() - StartTime;
    if (!FramePath.IsEmpty() && !Requested && Elapsed > 20.0)
    {
        Requested = true;
        FScreenshotRequest::RequestScreenshot(FramePath, false, false);
        UE_LOG(LogTemp, Display, TEXT("RABBIT_SMOKE_FRAME_REQUESTED"));
    }
    if (Requested && IFileManager::Get().FileSize(*FramePath) > 0)
    {
        UE_LOG(LogTemp, Display, TEXT("RABBIT_SMOKE_FRAME_WRITTEN"));
        FPlatformMisc::RequestExit(false);
    }
    if (!FramePath.IsEmpty() && Elapsed > 120.0)
    {
        UE_LOG(LogTemp, Error, TEXT("RABBIT_SMOKE_FRAME_TIMEOUT"));
        FPlatformMisc::RequestExitWithStatus(false, 1);
    }
}
