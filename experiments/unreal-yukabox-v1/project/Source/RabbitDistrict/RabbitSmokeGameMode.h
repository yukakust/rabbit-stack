#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "RabbitSmokeGameMode.generated.h"

// Controlled baseline. No network endpoint, LLM code execution or Dell transport.
UCLASS()
class ARabbitSmokeGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ARabbitSmokeGameMode();
    virtual void StartPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
    FString FramePath;
    double StartTime = 0;
    bool Requested = false;
};
