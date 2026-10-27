$ErrorActionPreference = "Stop"

$composeFile = Join-Path $PSScriptRoot "compose.yaml"
$cleanupScript = Join-Path $PSScriptRoot "cleanup_compose.py"
$dockerPreflight = Join-Path $PSScriptRoot "verify_docker_context.py"
$dockerGuardTests = Join-Path $PSScriptRoot "test_docker_context.py"
$runId = [Guid]::NewGuid().ToString("N")
$project = "editorial-poc-$runId"
$randomBytes = New-Object byte[] 48
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($randomBytes)
$rootPassword = [Convert]::ToBase64String($randomBytes).Replace("+", "-").Replace("/", "_").TrimEnd([char]'=')
$rng.Dispose()
$rootUsername = "pocroot"
$exitCode = 1
$resourcesMayExist = $false
$originalEnvironment = @{}

$values = @{
    EDITORIAL_POC_DISPOSABLE = "1"
    EDITORIAL_POC_RUN_ID = $runId
    EDITORIAL_POC_PROJECT = $project
    EDITORIAL_POC_MONGO_HOST = "mongo"
    EDITORIAL_POC_MONGO_PORT = "27017"
    EDITORIAL_POC_ROOT_USERNAME = $rootUsername
    EDITORIAL_POC_ROOT_PASSWORD = $rootPassword
}
foreach ($name in $values.Keys) {
    $originalEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
    [Environment]::SetEnvironmentVariable($name, $values[$name], "Process")
}

try {
    if ($env:MONGO_URL -or $env:MONGO_URL_TEST -or $env:DATABASE_URL -or $env:EDITORIAL_POC_MONGO_URI) {
        throw "Harness recusado: variável de conexão preexistente detectada."
    }
    & python $dockerGuardTests
    if ($LASTEXITCODE -ne 0) {
        throw "Testes da barreira de contexto Docker falharam."
    }
    & python $dockerPreflight
    if ($LASTEXITCODE -ne 0) {
        throw "Docker local Linux indisponível ou contexto não permitido. Nenhum serviço foi iniciado."
    }
    & docker compose version *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose indisponível."
    }
    $existingContainers = & docker ps -aq --filter "label=com.docker.compose.project=$project"
    $existingNetworks = & docker network ls -q --filter "label=com.docker.compose.project=$project"
    $existingVolumes = & docker volume ls -q --filter "label=com.docker.compose.project=$project"
    if ($existingContainers -or $existingNetworks -or $existingVolumes) {
        throw "Identidade aleatória do projeto já possui recursos; execução recusada."
    }

    & docker compose --project-name $project --file $composeFile config --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Configuração Compose inválida."
    }
    & docker compose --project-name $project --file $composeFile config --format json |
        python (Join-Path $PSScriptRoot "validate_compose.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Contrato de isolamento Compose inválido."
    }
    $resourcesMayExist = $true
    & docker compose --project-name $project --file $composeFile up --build --abort-on-container-exit --exit-code-from harness harness
    $exitCode = $LASTEXITCODE
}
catch {
    Write-Error $_
    $exitCode = 1
}
finally {
    if ($resourcesMayExist -and (Get-Command docker -ErrorAction SilentlyContinue)) {
        & python $cleanupScript --compose-file $composeFile
        if ($LASTEXITCODE -ne 0 -and $exitCode -eq 0) {
            $exitCode = 3
        }
    }
    foreach ($name in $values.Keys) {
        [Environment]::SetEnvironmentVariable($name, $originalEnvironment[$name], "Process")
    }
    $rootPassword = $null
    [Array]::Clear($randomBytes, 0, $randomBytes.Length)
    $values["EDITORIAL_POC_ROOT_PASSWORD"] = $null
    $values.Clear()
    $originalEnvironment.Clear()
}

exit $exitCode
