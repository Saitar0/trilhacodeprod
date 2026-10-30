$ErrorActionPreference = "Stop"

$composeFile = Join-Path $PSScriptRoot "compose.yaml"
$dockerGuard = Join-Path (Split-Path $PSScriptRoot -Parent) "editorial-generations\verify_docker_context.py"
$runId = [Guid]::NewGuid().ToString("N")
$project = "beta8-1-$runId"
$networkName = "beta8-1-$runId-net"
$harnessImageName = "$project-harness"
$mongoImage = "mongo:7.0.43"
$expectedMongoImageId = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
$containerId = ""
$networkId = ""
$keyPath = Join-Path ([System.IO.Path]::GetTempPath()) "trilhacode-beta8-1-$runId-keyfile"
$randomBytes = New-Object byte[] 512
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($randomBytes)
$keyValue = [Convert]::ToBase64String($randomBytes)
$rng.Dispose()
$keyBytes = [System.Text.Encoding]::UTF8.GetBytes($keyValue)
[System.IO.File]::WriteAllBytes($keyPath, $keyBytes)
$passwordBytes = New-Object byte[] 32
$passwordRng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$passwordRng.GetBytes($passwordBytes)
$rootPassword = [BitConverter]::ToString($passwordBytes).Replace("-", "").ToLowerInvariant()
$passwordRng.Dispose()
$rootUsername = "beta8-root"
$resourcesMayExist = $false
$preflightPassed = $false
$exitCode = 1
$environmentValues = @{
    BETA8_DISPOSABLE = "1"
    BETA8_RUN_ID = $runId
    BETA8_DOCKER_PRECHECKED = "false"
    BETA8_DOCKER_CONTAINER_ID = ""
    BETA8_DOCKER_NETWORK_ID = ""
    BETA8_MONGO_HOST = "mongo"
    BETA8_MONGO_PORT = "27017"
    BETA8_ROOT_USERNAME = $rootUsername
    BETA8_ROOT_PASSWORD = $rootPassword
    BETA8_MONGO_KEYFILE = $keyPath.Replace("\", "/")
}
$previousEnvironment = @{}
foreach ($name in $environmentValues.Keys) {
    $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
    [Environment]::SetEnvironmentVariable($name, $environmentValues[$name], "Process")
}

function Invoke-DockerJson([string[]]$Arguments) {
    $raw = & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Inspeção Docker falhou; execução encerrada." }
    return ($raw | ConvertFrom-Json)
}

function Assert-OwnedResources {
    $container = @(Invoke-DockerJson @("inspect", $script:containerId))
    if ($container.Count -ne 1) { throw "Identidade do contêiner Beta 8 não é única." }
    $item = $container[0]
    $labels = $item.Config.Labels
    if ($labels.'io.trilhacode.phase' -ne "beta8-1" -or $labels.'io.trilhacode.run' -ne $script:runId -or $labels.'io.trilhacode.role' -ne "mongo") {
        throw "Propriedade do contêiner Beta 8 não foi comprovada."
    }
    if ($item.Image -ne $script:expectedMongoImageId -or -not $item.State.Running) {
        throw "Imagem ou estado do MongoDB Beta 8 diverge do contrato."
    }
    $tmpfsPaths = @($item.HostConfig.Tmpfs.PSObject.Properties.Name)
    if ($item.Mounts.Count -ne 1 -or $item.Mounts[0].Destination -ne "/run/secrets/beta8-mongo-keyfile" -or $item.Mounts[0].RW -ne $false) {
        throw "Contêiner contém montagem não autorizada."
    }
    if (-not ($tmpfsPaths -contains "/data/db") -or -not ($tmpfsPaths -contains "/data/configdb") -or -not ($tmpfsPaths -contains "/run/mongo")) {
        throw "Armazenamento MongoDB não é exclusivamente temporário."
    }
    $bindings = $item.HostConfig.PortBindings
    if ($bindings -and @($bindings.PSObject.Properties | Where-Object { $_.Value })) {
        throw "Porta publicada detectada; MongoDB Beta 8 deve permanecer privado."
    }
    $attached = @($item.NetworkSettings.Networks.PSObject.Properties.Name)
    if ($attached.Count -ne 1 -or $attached[0] -ne $script:networkName) {
        throw "Rede do contêiner não corresponde à rede privada Beta 8."
    }
    $network = @(Invoke-DockerJson @("network", "inspect", $script:networkId))
    if ($network.Count -ne 1 -or $network[0].Name -ne $script:networkName -or $network[0].Internal -ne $true -or $network[0].Driver -ne "bridge") {
        throw "Rede interna Beta 8 não comprovada."
    }
    if ($network[0].Labels.'io.trilhacode.phase' -ne "beta8-1" -or $network[0].Labels.'io.trilhacode.run' -ne $script:runId) {
        throw "Marcadores de propriedade da rede Beta 8 divergentes."
    }
    $attachedOutput = (& docker network inspect $script:networkId --format '{{range $id, $c := .Containers}}{{$id}} {{end}}').Trim()
    $attachedIds = @($attachedOutput -split '\s+' | Where-Object { $_ })
    if ($attachedIds.Count -ne 1 -or $attachedIds[0] -ne $script:containerId) {
        throw "A rede contém participante não pertencente ao preflight Beta 8."
    }
}

function Assert-OwnedForCleanup {
    if ($script:containerId -notmatch '^[a-f0-9]{64}$') {
        $script:containerId = (& docker compose --project-name $script:project --file $script:composeFile ps -aq --no-trunc mongo).Trim()
    }
    if ($script:networkId -notmatch '^[a-f0-9]{64}$') {
        $script:networkId = (& docker network inspect $script:networkName --format '{{.Id}}').Trim()
    }
    if ($script:containerId -notmatch '^[a-f0-9]{64}$' -or $script:networkId -notmatch '^[a-f0-9]{64}$') {
        throw "IDs exatos para cleanup não foram comprovados; recursos preservados."
    }
    $container = @(Invoke-DockerJson @("inspect", $script:containerId))
    $network = @(Invoke-DockerJson @("network", "inspect", $script:networkId))
    if ($container.Count -ne 1 -or $network.Count -ne 1) { throw "IDs de cleanup não são únicos." }
    $containerLabels = $container[0].Config.Labels
    $networkLabels = $network[0].Labels
    if (
        $containerLabels.'io.trilhacode.phase' -ne "beta8-1" -or
        $containerLabels.'io.trilhacode.run' -ne $script:runId -or
        $containerLabels.'io.trilhacode.role' -ne "mongo" -or
        $containerLabels.'com.docker.compose.project' -ne $script:project -or
        $network[0].Name -ne $script:networkName -or
        $networkLabels.'io.trilhacode.phase' -ne "beta8-1" -or
        $networkLabels.'io.trilhacode.run' -ne $script:runId -or
        $networkLabels.'com.docker.compose.project' -ne $script:project
    ) {
        throw "Labels/identidades não comprovam propriedade Beta 8; cleanup recusado."
    }
    $projectContainers = @(& docker ps -aq --no-trunc --filter "label=com.docker.compose.project=$script:project")
    $projectNetworks = @(& docker network ls -q --no-trunc --filter "label=com.docker.compose.project=$script:project")
    $projectVolumes = @(& docker volume ls -q --filter "label=com.docker.compose.project=$script:project")
    $attachedOutput = (& docker network inspect $script:networkId --format '{{range $id, $c := .Containers}}{{$id}} {{end}}').Trim()
    $attachedIds = @($attachedOutput -split '\s+' | Where-Object { $_ })
    if (
        $projectContainers.Count -ne 1 -or $projectContainers[0].Trim() -ne $script:containerId -or
        $projectNetworks.Count -ne 1 -or $projectNetworks[0].Trim() -ne $script:networkId -or
        $projectVolumes.Count -ne 0 -or $attachedIds.Count -gt 1 -or
        ($attachedIds.Count -eq 1 -and $attachedIds[0] -ne $script:containerId)
    ) {
        throw "Projeto Docker contém recursos inesperados; cleanup recusado."
    }
}

function Remove-OwnedHarnessImage {
    $imageIds = @(& docker image ls --quiet --no-trunc $script:harnessImageName)
    if ($LASTEXITCODE -ne 0) { throw "Inspeção da imagem temporária falhou; imagem preservada." }
    $imageIds = @($imageIds | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($imageIds.Count -eq 0) { return }
    if ($imageIds.Count -ne 1 -or $imageIds[0] -notmatch '^sha256:[a-f0-9]{64}$') {
        throw "Imagem do harness não é única; remoção recusada."
    }
    $image = @(Invoke-DockerJson @("image", "inspect", $imageIds[0]))
    if ($image.Count -ne 1) { throw "Identidade da imagem do harness não é única." }
    $labels = $image[0].Config.Labels
    $tags = @($image[0].RepoTags)
    if (
        $labels.'io.trilhacode.phase' -ne "beta8-1" -or
        $labels.'io.trilhacode.run' -ne $script:runId -or
        $labels.'io.trilhacode.role' -ne "harness" -or
        -not ($tags -contains "$($script:harnessImageName):latest")
    ) {
        throw "Marcadores da imagem não comprovam propriedade Beta 8; remoção recusada."
    }
    & docker image rm $imageIds[0]
    if ($LASTEXITCODE -ne 0) { throw "Imagem Beta 8 não foi removida." }
    if (@(& docker image ls --quiet --no-trunc $script:harnessImageName)) {
        throw "Imagem Beta 8 permaneceu após a limpeza verificada."
    }
}

try {
    if (Get-ChildItem Env: | Where-Object { $_.Name -match '^DOCKER_(HOST|CONTEXT|TLS_VERIFY|CERT_PATH)$' -and $_.Value }) {
        throw "Overrides Docker detectados; nenhuma infraestrutura foi iniciada."
    }
    & python $dockerGuard
    if ($LASTEXITCODE -ne 0) { throw "Contexto Docker local não homologado." }
    if ((& docker image inspect $mongoImage --format '{{.Id}}') -ne $expectedMongoImageId) {
        throw "A imagem MongoDB 7.0.43 pinada não está disponível localmente."
    }
    & docker compose --project-name $project --file $composeFile config --quiet
    if ($LASTEXITCODE -ne 0) { throw "Contrato Compose Beta 8 inválido." }
    $config = (& docker compose --project-name $project --file $composeFile config --format json | ConvertFrom-Json)
    if ($LASTEXITCODE -ne 0 -or $config.services.mongo.ports -or $config.services.mongo.volumes -or $config.networks.beta8_1_private.internal -ne $true) {
        throw "Compose Beta 8 não satisfaz os limites de porta, volume e rede."
    }

    $existingContainers = & docker ps -aq --filter "label=com.docker.compose.project=$project"
    $existingNetworks = & docker network ls -q --filter "label=com.docker.compose.project=$project"
    $existingVolumes = & docker volume ls -q --filter "label=com.docker.compose.project=$project"
    if ($existingContainers -or $existingNetworks -or $existingVolumes) {
        throw "O nome aleatório de execução já possui recursos; reutilização recusada."
    }

    $resourcesMayExist = $true
    & docker compose --project-name $project --file $composeFile up -d mongo
    if ($LASTEXITCODE -ne 0) { throw "MongoDB Beta 8 não iniciou; a prova foi bloqueada." }
    $containerId = (& docker compose --project-name $project --file $composeFile ps -q --no-trunc mongo).Trim()
    $networkId = (& docker network inspect $networkName --format '{{.Id}}').Trim()
    if ($LASTEXITCODE -ne 0 -or $containerId -notmatch '^[a-f0-9]{64}$' -or $networkId -notmatch '^[a-f0-9]{64}$') {
        throw "Identidades Docker Beta 8 incompletas; nenhum teste persistente será executado."
    }
    Assert-OwnedResources
    $preflightPassed = $true
    [Environment]::SetEnvironmentVariable("BETA8_DOCKER_PRECHECKED", "true", "Process")
    [Environment]::SetEnvironmentVariable("BETA8_DOCKER_CONTAINER_ID", $containerId, "Process")
    [Environment]::SetEnvironmentVariable("BETA8_DOCKER_NETWORK_ID", $networkId, "Process")
    Write-Output "Gate de isolamento Beta 8 aprovado para execução $($runId.Substring(0, 8)); credenciais omitidas."

    & docker compose --project-name $project --file $composeFile run --rm harness
    $exitCode = $LASTEXITCODE
}
catch {
    Write-Error $_
    $exitCode = 1
}
finally {
    if ($resourcesMayExist) {
        try {
            Assert-OwnedForCleanup
            & docker compose --project-name $project --file $composeFile down
            if ($LASTEXITCODE -ne 0) { throw "Cleanup Compose Beta 8 falhou." }
            Remove-OwnedHarnessImage
            if ((& docker ps -aq --filter "id=$containerId") -or (& docker network ls -q --filter "id=$networkId")) {
                throw "Recursos Beta 8 permaneceram após cleanup."
            }
            Remove-Item -LiteralPath $keyPath -Force
            Write-Output "Recursos MongoDB e rede Beta 8 removidos após revalidação de propriedade."
        }
        catch {
            Write-Error $_
            $exitCode = 3
        }
    }
    if (Test-Path -LiteralPath $keyPath) {
        Remove-Item -LiteralPath $keyPath -Force
    }
    foreach ($name in $environmentValues.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], "Process")
    }
    [Array]::Clear($randomBytes, 0, $randomBytes.Length)
    [Array]::Clear($keyBytes, 0, $keyBytes.Length)
    [Array]::Clear($passwordBytes, 0, $passwordBytes.Length)
    $rootPassword = $null
    $keyValue = $null
    $environmentValues.Clear()
    $previousEnvironment.Clear()
}

exit $exitCode
