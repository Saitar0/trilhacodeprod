$ErrorActionPreference = "Stop"

$composeFile = Join-Path $PSScriptRoot "compose.yaml"
$dockerGuard = Join-Path (Split-Path $PSScriptRoot -Parent) "editorial-generations\verify_docker_context.py"
$runId = [Guid]::NewGuid().ToString("N")
$stageRunId = [Guid]::NewGuid().ToString("N")
$project = "beta9-$runId"
$networkName = "$project-net"
$imageName = "$project-processes:latest"
$mongoImage = "mongo:7.0.43"
$expectedMongoImageId = "sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b"
$containerId = ""
$networkId = ""
$apiContainerId = ""
$authorityContainerId = ""
$sourceSeederContainerId = ""
$webContainerId = ""
$sourceSnapshot = Join-Path ([System.IO.Path]::GetTempPath()) "trilhacode-beta9-source-$runId"
$authorityOriginalPid = 0
$verifierProcess = $null
$verifierStdout = Join-Path ([System.IO.Path]::GetTempPath()) "trilhacode-beta9-$runId-verifier.out"
$verifierStderr = Join-Path ([System.IO.Path]::GetTempPath()) "trilhacode-beta9-$runId-verifier.err"
$handledRestarts = [System.Collections.Generic.HashSet[string]]::new()
$keyPath = Join-Path ([System.IO.Path]::GetTempPath()) "trilhacode-beta9-$runId-keyfile"
$keyBytes = New-Object byte[] 512
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($keyBytes)
$rng.Dispose()
[System.IO.File]::WriteAllBytes($keyPath, [System.Text.Encoding]::UTF8.GetBytes([Convert]::ToBase64String($keyBytes)))

function New-HexSecret([int]$ByteCount) {
    $bytes = New-Object byte[] $ByteCount
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $generator.GetBytes($bytes)
    $generator.Dispose()
    $value = [BitConverter]::ToString($bytes).Replace("-", "").ToLowerInvariant()
    [Array]::Clear($bytes, 0, $bytes.Length)
    return $value
}

$rootUsername = "beta8-root"
$rootPassword = New-HexSecret 32
$apiPassword = New-HexSecret 32
$authorityPassword = New-HexSecret 32
$stageWritePassword = New-HexSecret 32
$stageReadPassword = New-HexSecret 32
$stageOwnerToken = New-HexSecret 32
$serviceSecret = New-HexSecret 48
$operationKey = New-HexSecret 48
$jwtSecret = New-HexSecret 48
$studentPassword = New-HexSecret 32
$reviewerPassword = New-HexSecret 32
$unscopedPassword = New-HexSecret 32
$adminPassword = New-HexSecret 32
$dbName = "editorial_revision_test_c10_c11_c12_b83_$($runId.Substring(0, 12))"
$previewDatabaseName = "beta9p_$($runId.Substring(0, 12))"
$stageDbName = "beta5_$stageRunId"
$rootUri = "mongodb://$rootUsername`:$rootPassword@mongo:27017/admin?authSource=admin&replicaSet=rsB83&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
$apiUri = "mongodb://beta8-3-api`:$apiPassword@mongo:27017/$dbName`?authSource=$dbName&replicaSet=rsB83&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
$authorityUri = "mongodb://beta8-3-authority`:$authorityPassword@mongo:27017/$dbName`?authSource=$dbName&replicaSet=rsB83&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
$stageWriteUri = "mongodb://beta8-3-stager`:$stageWritePassword@mongo:27017/$stageDbName`?authSource=$stageDbName&replicaSet=rsB83&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
$stageReadUri = "mongodb://beta8-3-stage-reader`:$stageReadPassword@mongo:27017/$stageDbName`?authSource=$stageDbName&replicaSet=rsB83&serverSelectionTimeoutMS=8000&connectTimeoutMS=8000"
$editorId = [Guid]::NewGuid().ToString("N").Substring(0, 24)
$noGrantId = [Guid]::NewGuid().ToString("N").Substring(0, 24)
$adminId = [Guid]::NewGuid().ToString("N").Substring(0, 24)
$nodeId = [Guid]::NewGuid().ToString("N").Substring(0, 24)
$blockId = [Guid]::NewGuid().ToString("N").Substring(0, 24)
$studentEmail = "student-$($runId.Substring(0, 8))@example.com"
$reviewerEmail = "reviewer-$($runId.Substring(0, 8))@example.com"
$unscopedEmail = "unscoped-$($runId.Substring(0, 8))@example.com"
$seedAdminEmail = "importer-$($runId.Substring(0, 8))@example.com"
$environmentValues = @{
    BETA9_RUN_ID = $runId
    BETA9_PREVIEW_DATABASE = $previewDatabaseName
    BETA9_PREVIEW_BATCH_ID = ""
    BETA9_PRIVATE_TRACK_ID = ""
    BETA9_STUDENT_EMAIL = $studentEmail
    BETA9_STUDENT_PASSWORD = $studentPassword
    BETA9_REVIEWER_EMAIL = $reviewerEmail
    BETA9_REVIEWER_PASSWORD = $reviewerPassword
    BETA9_UNSCOPED_EMAIL = $unscopedEmail
    BETA9_UNSCOPED_PASSWORD = $unscopedPassword
    BETA9_ADMIN_EMAIL = $seedAdminEmail
    BETA9_ADMIN_PASSWORD = $adminPassword
    BETA8_3_RUN_ID = $runId
    BETA8_3_STAGE_RUN_ID = $stageRunId
    BETA8_3_DB_NAME = $dbName
    BETA8_3_ROOT_USERNAME = $rootUsername
    BETA8_3_ROOT_PASSWORD = $rootPassword
    BETA8_3_ROOT_URI = $rootUri
    BETA8_3_API_PASSWORD = $apiPassword
    BETA8_3_AUTHORITY_PASSWORD = $authorityPassword
    BETA8_3_API_MONGO_URI = $apiUri
    BETA8_3_AUTHORITY_MONGO_URI = $authorityUri
    BETA8_3_STAGE_OWNER_TOKEN = $stageOwnerToken
    BETA8_3_STAGE_WRITE_PASSWORD = $stageWritePassword
    BETA8_3_STAGE_READ_PASSWORD = $stageReadPassword
    BETA8_3_STAGE_WRITE_URI = $stageWriteUri
    BETA8_3_STAGE_READ_URI = $stageReadUri
    BETA8_3_SERVICE_SECRET_HEX = $serviceSecret
    BETA8_3_STAGER_SECRET_HEX = (New-HexSecret 48)
    BETA8_3_OPERATION_KEY_HEX = $operationKey
    BETA8_3_JWT_SECRET = $jwtSecret
    BETA8_3_MONGO_KEYFILE = $keyPath.Replace("\", "/")
    BETA8_3_IMAGE_NAME = $imageName
    BETA8_3_EDITOR_ID = $editorId
    BETA8_3_EDITOR_EMAIL = "editor-$($runId.Substring(0, 8))@example.com"
    BETA8_3_NO_GRANT_ID = $noGrantId
    BETA8_3_NO_GRANT_EMAIL = "no-grant-$($runId.Substring(0, 8))@example.com"
    BETA8_3_ADMIN_ID = $adminId
    BETA8_3_ADMIN_EMAIL = "admin-$($runId.Substring(0, 8))@example.com"
    BETA8_3_NODE_ID = $nodeId
    BETA8_3_BLOCK_ID = $blockId
    BETA8_3_DOCKER_PRECHECKED = "false"
    BETA8_3_DOCKER_CONTAINER_ID = ""
    BETA8_3_DOCKER_NETWORK_ID = ""
}
$previousEnvironment = @{}
foreach ($name in $environmentValues.Keys) {
    $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
    [Environment]::SetEnvironmentVariable($name, $environmentValues[$name], "Process")
}
$resourcesMayExist = $false
$imageMayExist = $false
$exitCode = 1

function Invoke-DockerJson([string[]]$Arguments) {
    $raw = & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Inspeção Docker falhou; execução bloqueada." }
    return ($raw | ConvertFrom-Json)
}

function Assert-OwnedMongo {
    $items = @(Invoke-DockerJson @("inspect", $script:containerId))
    if ($items.Count -ne 1) { throw "Identidade MongoDB Beta 9 não é única." }
    $item = $items[0]
    $labels = $item.Config.Labels
    if (
        $labels.'io.trilhacode.phase' -ne "beta9" -or
        $labels.'io.trilhacode.run' -ne $script:runId -or
        $labels.'io.trilhacode.role' -ne "mongo" -or
        $labels.'com.docker.compose.project' -ne $script:project -or
        $item.Image -ne $script:expectedMongoImageId -or -not $item.State.Running
    ) { throw "Propriedade, imagem ou estado do MongoDB não foi comprovado." }
    $mounts = @($item.Mounts)
    if ($mounts.Count -ne 1 -or $mounts[0].Destination -ne "/run/secrets/beta8-mongo-keyfile" -or $mounts[0].RW) {
        throw "Montagem inesperada detectada no MongoDB Beta 9."
    }
    $tmpfs = @($item.HostConfig.Tmpfs.PSObject.Properties.Name)
    if (-not ($tmpfs -contains "/data/db") -or -not ($tmpfs -contains "/data/configdb") -or -not ($tmpfs -contains "/run/mongo")) {
        throw "MongoDB Beta 9 não utiliza armazenamento exclusivamente temporário."
    }
    if ($item.HostConfig.PortBindings -and @($item.HostConfig.PortBindings.PSObject.Properties | Where-Object { $_.Value })) {
        throw "Porta pública detectada no MongoDB Beta 9."
    }
    $attached = @($item.NetworkSettings.Networks.PSObject.Properties.Name)
    if ($attached.Count -ne 1 -or $attached[0] -ne $script:networkName) {
        throw "Rede do MongoDB Beta 9 diverge do harness."
    }
    $networks = @(Invoke-DockerJson @("network", "inspect", $script:networkId))
    if (
        $networks.Count -ne 1 -or $networks[0].Name -ne $script:networkName -or
        $networks[0].Internal -ne $true -or $networks[0].Driver -ne "bridge" -or
        $networks[0].Labels.'io.trilhacode.phase' -ne "beta9" -or
        $networks[0].Labels.'io.trilhacode.run' -ne $script:runId
    ) { throw "Propriedade e isolamento da rede não foram comprovados." }
    $attachedOutput = (& docker network inspect $script:networkId --format '{{range $id, $c := .Containers}}{{$id}} {{end}}').Trim()
    $attachedIds = @($attachedOutput -split '\s+' | Where-Object { $_ })
    if ($attachedIds.Count -ne 1 -or $attachedIds[0] -ne $script:containerId) {
        throw "A rede MongoDB tem participante inesperado durante o gate inicial."
    }
}

function Assert-ProjectOwnership {
    $containers = @(& docker ps -aq --no-trunc --filter "label=com.docker.compose.project=$script:project")
    if ($LASTEXITCODE -ne 0 -or $containers.Count -lt 1) { throw "Contêineres do harness não puderam ser enumerados." }
    $allowedRoles = @("mongo", "authority", "api", "verifier", "source-seeder", "web")
    $ids = @($containers | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($ids.Count -lt 1 -or $ids.Count -gt 6 -or -not ($ids -contains $script:containerId)) {
        throw "Projeto Docker contém quantidade inesperada de contêineres; cleanup recusado."
    }
    $seenRoles = @{}
    foreach ($id in $ids) {
        $item = @(Invoke-DockerJson @("inspect", $id))[0]
        $labels = $item.Config.Labels
        $role = $labels.'io.trilhacode.role'
        if (
            $labels.'io.trilhacode.phase' -ne "beta9" -or
            $labels.'io.trilhacode.run' -ne $script:runId -or
            $labels.'com.docker.compose.project' -ne $script:project -or
            $role -notin $allowedRoles -or $seenRoles.ContainsKey($role)
        ) { throw "Um contêiner do projeto não pertence ao harness Beta 9; cleanup recusado." }
        $seenRoles[$role] = $id
        $expectedId = switch ($role) {
            "mongo" { $script:containerId }
            "api" { $script:apiContainerId }
            "authority" { $script:authorityContainerId }
            "source-seeder" { $script:sourceSeederContainerId }
            "web" { $script:webContainerId }
        }
        if ($expectedId -and $expectedId -ne $id) {
            throw "Identidade do contêiner diverge do papel declarado; cleanup recusado."
        }
        if ($item.HostConfig.PortBindings -and @($item.HostConfig.PortBindings.PSObject.Properties | Where-Object { $_.Value })) {
            throw "Porta publicada detectada; cleanup automático recusado."
        }
        $mounts = @($item.Mounts)
        if ($role -eq "mongo") {
            if (
                $mounts.Count -ne 1 -or
                $mounts[0].Destination -ne "/run/secrets/beta8-mongo-keyfile" -or
                $mounts[0].RW
            ) { throw "Montagem inesperada detectada no MongoDB; cleanup recusado." }
        } elseif ($mounts.Count -gt 0) {
            throw "Mount persistente ou externo detectado em serviço; cleanup recusado."
        }
    }
    if (-not $seenRoles.ContainsKey("mongo")) { throw "MongoDB não pertence ao conjunto próprio; cleanup recusado." }
    $networkIds = @(& docker network ls -q --no-trunc --filter "label=com.docker.compose.project=$script:project")
    if ($LASTEXITCODE -ne 0 -or $networkIds.Count -ne 1 -or $networkIds[0].Trim() -ne $script:networkId) {
        throw "Rede do projeto não é única ou não corresponde ao gate."
    }
    $network = @(Invoke-DockerJson @("network", "inspect", $script:networkId))[0]
    if (
        $network.Name -ne $script:networkName -or $network.Internal -ne $true -or
        $network.Labels.'io.trilhacode.phase' -ne "beta9" -or
        $network.Labels.'io.trilhacode.run' -ne $script:runId
    ) { throw "Rede não pertence comprovadamente ao harness; cleanup recusado." }
    $attachedOutput = (& docker network inspect $script:networkId --format '{{range $id, $c := .Containers}}{{$id}} {{end}}').Trim()
    $attachedIds = @($attachedOutput -split '\s+' | Where-Object { $_ })
    if (
        @($attachedIds | Where-Object { $_ -notin $ids }).Count -gt 0 -or
        $script:containerId -notin $attachedIds
    ) {
        throw "A rede possui participante sem propriedade comprovada; cleanup recusado."
    }
    if (@(& docker volume ls -q --filter "label=com.docker.compose.project=$script:project")) {
        throw "Volume persistente detectado; cleanup automático recusado."
    }
}

function Assert-OwnedAuthority([bool]$MustBeRunning) {
    $items = @(Invoke-DockerJson @("inspect", $script:authorityContainerId))
    if ($items.Count -ne 1) { throw "Identidade do contêiner da autoridade não é única." }
    $item = $items[0]
    $publishedPorts = @($item.HostConfig.PortBindings.PSObject.Properties | Where-Object { $_.Value })
    if (
        $item.Config.Labels.'io.trilhacode.phase' -ne "beta9" -or
        $item.Config.Labels.'io.trilhacode.run' -ne $script:runId -or
        $item.Config.Labels.'io.trilhacode.role' -ne "authority" -or
        $item.Config.Labels.'com.docker.compose.project' -ne $script:project -or
        $publishedPorts.Count -gt 0 -or $item.Mounts.Count -gt 0
    ) { throw "Propriedade ou isolamento da autoridade não foi comprovado." }
    if ($MustBeRunning -and -not $item.State.Running) {
        throw "Autoridade não está em execução no ponto de controle."
    }
    return $item
}

function Stop-VerifiedAuthority([string]$Label) {
    Assert-ProjectOwnership
    $authority = Assert-OwnedAuthority $true
    $oldPid = [int]$authority.State.Pid
    if ($oldPid -le 0) { throw "PID da autoridade não pôde ser verificado." }
    $script:authorityOriginalPid = $oldPid
    & docker kill --signal KILL $script:authorityContainerId | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Interrupção do contêiner próprio da autoridade falhou." }
    $deadline = [DateTime]::UtcNow.AddSeconds(15)
    do {
        Start-Sleep -Milliseconds 100
        $stopped = Assert-OwnedAuthority $false
    } while ($stopped.State.Running -and [DateTime]::UtcNow -lt $deadline)
    if ($stopped.State.Running) { throw "Contêiner da autoridade não encerrou após SIGKILL." }
    if ($stopped.Id -ne $script:authorityContainerId) { throw "Identidade mudou durante a interrupção." }
    Write-Output "Autoridade $Label interrompida; aguardando confirmação HTTP da indisponibilidade."
}

function Start-VerifiedAuthority([string]$Label) {
    $stopped = Assert-OwnedAuthority $false
    if ($stopped.State.Running) { throw "Autoridade não ficou parada antes do restart." }
    & docker start $script:authorityContainerId | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Reinício do contêiner próprio da autoridade falhou." }
    $deadline = [DateTime]::UtcNow.AddSeconds(30)
    do {
        Start-Sleep -Milliseconds 100
        $started = Assert-OwnedAuthority $false
        if ($started.State.Running -and [int]$started.State.Pid -gt 0 -and [int]$started.State.Pid -ne $script:authorityOriginalPid) { break }
    } while ([DateTime]::UtcNow -lt $deadline)
    if (-not $started.State.Running -or [int]$started.State.Pid -eq $script:authorityOriginalPid) { throw "PID da autoridade não mudou após restart real." }
    Assert-ProjectOwnership
    Write-Output "Restart real confirmado para $Label; autoridade PID $script:authorityOriginalPid -> $($started.State.Pid)."
}

function Invoke-AuthorityRestartVerifier {
    if (Test-Path -LiteralPath $verifierStdout) { Remove-Item -LiteralPath $verifierStdout -Force }
    if (Test-Path -LiteralPath $verifierStderr) { Remove-Item -LiteralPath $verifierStderr -Force }
    $dockerPath = (Get-Command docker).Source
    $arguments = @("compose", "--project-name", $project, "--file", $composeFile, "run", "--rm", "verifier")
    $argumentLine = ($arguments | ForEach-Object {
        if ($_ -match '\s') { '"' + $_.Replace('"', '\"') + '"' } else { $_ }
    }) -join ' '
    $script:verifierProcess = Start-Process -FilePath $dockerPath -ArgumentList $argumentLine `
        -RedirectStandardOutput $verifierStdout -RedirectStandardError $verifierStderr `
        -PassThru -WindowStyle Hidden
    $script:verifierProcess | Out-Null
    $deadline = [DateTime]::UtcNow.AddMinutes(12)
    $lineCursor = 0
    $pendingRestart = $null
    $verifierComplete = $false
    while ([DateTime]::UtcNow -lt $deadline) {
        $script:verifierProcess.Refresh()
        $lines = @()
        if (Test-Path -LiteralPath $verifierStdout) { $lines = @(Get-Content -LiteralPath $verifierStdout) }
        while ($lineCursor -lt $lines.Count) {
            $line = [string]$lines[$lineCursor]
            $lineCursor++
            if ($line -match '^BETA8_4_RESTART_AUTHORITY:([a-z_]+):pause$') {
                $label = $Matches[1]
                if ($pendingRestart) { throw "Novo pedido de restart antes da confirmação anterior." }
                if (-not $handledRestarts.Add($label)) { throw "Pedido de restart repetido: $label." }
                $pendingRestart = $label
                Stop-VerifiedAuthority $label
            } elseif ($line -match '^BETA8_4_RESTART_AUTHORITY:([a-z_]+):down$') {
                $label = $Matches[1]
                if ($pendingRestart -ne $label) { throw "Sinal de indisponibilidade sem pedido próprio." }
                Start-VerifiedAuthority $label
                $pendingRestart = $null
            } elseif ($line -eq 'BETA9_VERIFIER_COMPLETE') {
                $verifierComplete = $true
                Write-Output $line
            } elseif ($line -match '^BETA8_4_|^BETA8_3_') {
                Write-Output $line
            }
        }
        if ($script:verifierProcess.HasExited) { break }
        Start-Sleep -Milliseconds 100
    }
    # The verifier may print its final pass markers and exit between polling
    # iterations. Drain the redirected file once more after process exit so
    # the report does not lose the last staging-recovery evidence line.
    if (Test-Path -LiteralPath $verifierStdout) {
        $finalLines = @(Get-Content -LiteralPath $verifierStdout)
        while ($lineCursor -lt $finalLines.Count) {
            $line = [string]$finalLines[$lineCursor]
            $lineCursor++
            if ($line -eq 'BETA9_VERIFIER_COMPLETE') {
                $verifierComplete = $true
                Write-Output $line
            } elseif ($line -match '^BETA8_4_|^BETA8_3_') { Write-Output $line }
        }
    }
    $script:verifierProcess.Refresh()
    if (-not $script:verifierProcess.HasExited) {
        Stop-Process -Id $script:verifierProcess.Id -Force
        throw "Verificador persistente excedeu o limite de tempo."
    }
    if ($pendingRestart) { throw "Autoridade não foi observada indisponível após pedido $pendingRestart." }
    $verifierExitCode = $script:verifierProcess.ExitCode
    if (-not $verifierComplete -or ($null -ne $verifierExitCode -and $verifierExitCode -ne 0)) {
        if (Test-Path -LiteralPath $verifierStderr) { Get-Content -LiteralPath $verifierStderr | Write-Output }
        $serviceLogs = (& docker compose --project-name $project --file $composeFile logs --no-color api authority 2>&1) -join "`n"
        foreach ($entry in $environmentValues.GetEnumerator()) {
            if ($entry.Key -match "PASSWORD|SECRET|URI|TOKEN|KEY" -and $entry.Value) {
                $serviceLogs = $serviceLogs.Replace([string]$entry.Value, "[redacted]")
            }
        }
        Write-Output "API/authority startup diagnostics (credentials redacted):"
        ($serviceLogs -split "`r?`n" | Select-String -Pattern "Traceback|Error|Exception|startup|Application|RuntimeError|ImportError|denied|failed" -Context 1,2 | Select-Object -Last 24) | ForEach-Object { Write-Output $_.ToString() }
        $exitDescription = if ($null -eq $verifierExitCode) { "indisponível" } else { [string]$verifierExitCode }
        throw "Prova HTTP/MongoDB Beta 9 falhou (completude=$verifierComplete; código de saída=$exitDescription)."
    }
    if ($handledRestarts.Count -ne 3) { throw "Esperados três reinícios reais; observados $($handledRestarts.Count)." }
    Write-Output "BETA8_4_RESTART_AND_RECOVERY: PASS; three owned authority container restarts observed with persisted reconciliation."
    Assert-ProjectOwnership
}

function Remove-OwnedImage {
    $imageIds = @(& docker image ls --quiet --no-trunc $script:imageName)
    if ($LASTEXITCODE -ne 0) { throw "Imagem do harness não pôde ser inspecionada." }
    $imageIds = @($imageIds | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($imageIds.Count -eq 0) { return }
    if ($imageIds.Count -ne 1) { throw "Imagem Beta 9 não é única; remoção recusada." }
    $image = @(Invoke-DockerJson @("image", "inspect", $imageIds[0]))[0]
    if (
        $image.Config.Labels.'io.trilhacode.phase' -ne "beta9" -or
        $image.Config.Labels.'io.trilhacode.run' -ne $script:runId -or
        -not (@($image.RepoTags) -contains $script:imageName)
    ) { throw "Marcadores da imagem não comprovam propriedade; remoção recusada." }
    & docker image rm $imageIds[0]
    if ($LASTEXITCODE -ne 0) { throw "Imagem temporária Beta 9 não foi removida." }
}

try {
    if (Get-ChildItem Env: | Where-Object { $_.Name -match '^DOCKER_(HOST|CONTEXT|TLS_VERIFY|CERT_PATH)$' -and $_.Value }) {
        throw "Overrides Docker recusados; nenhum ambiente foi iniciado."
    }
    & python $dockerGuard
    if ($LASTEXITCODE -ne 0) { throw "Contexto Docker local não foi confirmado." }
    if ((& docker image inspect $mongoImage --format '{{.Id}}') -ne $expectedMongoImageId) {
        throw "Imagem MongoDB 7.0.43 pinada não está disponível localmente."
    }
    & docker compose --project-name $project --file $composeFile config --quiet
    if ($LASTEXITCODE -ne 0) { throw "Contrato Compose Beta 9 inválido." }
    $compose = (& docker compose --project-name $project --file $composeFile config --format json | ConvertFrom-Json)
    if ($LASTEXITCODE -ne 0) { throw "Compose Beta 9 não pôde ser inspecionado." }
    $compositionViolations = [System.Collections.Generic.List[string]]::new()
    $sourceSeederService = $compose.services.PSObject.Properties['source-seeder'].Value
    if ($compose.networks.beta8_3_private.internal -ne $true) { $compositionViolations.Add("rede não interna") }
    if ($compose.networks.beta8_3_private.driver -ne "bridge") { $compositionViolations.Add("driver de rede inesperado") }
    foreach ($serviceName in @("mongo", "api", "authority", "web", "browser", "source-seeder")) {
        $service = $compose.services.PSObject.Properties[$serviceName].Value
        if ($service.ports) { $compositionViolations.Add("porta publicada em $serviceName") }
        if ($service.volumes) { $compositionViolations.Add("volume persistente em $serviceName") }
    }
    if ($compose.services.api.environment.MONGO_URL -notmatch '^mongodb://beta8-3-api:') { $compositionViolations.Add("URI da API não usa identidade restrita") }
    if ($compose.services.authority.environment.MONGO_URL -notmatch '^mongodb://beta8-3-authority:') { $compositionViolations.Add("URI da autoridade não usa identidade editorial") }
    if ($compose.services.api.command -notcontains "test_support.beta9_integrated_api_server:app") { $compositionViolations.Add("API não inicia o wrapper de prévia Beta 9") }
    foreach ($secretName in @("BETA8_3_AUTHORITY_MONGO_URI", "BETA8_3_AUTHORITY_MONGO_PASSWORD", "BETA8_3_STAGE_READ_URI", "BETA8_3_STAGE_WRITE_URI", "BETA8_3_STAGER_SECRET_HEX", "BETA8_3_ROOT_URI", "BETA8_3_ROOT_PASSWORD", "BETA9_ADMIN_PASSWORD", "BETA9_STUDENT_PASSWORD")) {
        if ($compose.services.api.environment.$secretName) { $compositionViolations.Add("API recebeu segredo restrito: $secretName") }
    }
    foreach ($secretName in @("BETA8_3_API_MONGO_URI", "BETA8_3_ROOT_PASSWORD", "BETA8_3_STAGE_WRITE_URI", "BETA8_3_STAGE_WRITE_PASSWORD")) {
        if ($compose.services.authority.environment.$secretName) { $compositionViolations.Add("autoridade recebeu segredo fora do escopo: $secretName") }
    }
    $sourceSeederMongoUri = $sourceSeederService.environment.PSObject.Properties['MONGO_URL'].Value
    if ($sourceSeederMongoUri -notmatch '^mongodb://beta8-root:') { $compositionViolations.Add("seeder não recebeu identidade root sintética") }
    if ($compose.services.browser.environment.PLAYWRIGHT_BASE_URL -ne "http://web:3000") { $compositionViolations.Add("browser não está configurado para a UI interna") }
    if ($compose.services.web.environment.BETA9_FULLSTACK_TEST -ne "1") { $compositionViolations.Add("frontend não está no modo de teste integrado") }
    foreach ($serviceName in @("provisioner", "api", "source-seeder")) {
        $service = $compose.services.PSObject.Properties[$serviceName].Value
        if ($service.environment.BETA7_1_PREVIEW_DB_NAME -ne $previewDatabaseName) {
            $compositionViolations.Add("namespace de prévia não está fixado no serviço $serviceName")
        }
    }
    if ($compositionViolations.Count -gt 0) {
        throw "Composição Beta 9 não passou no gate: $($compositionViolations -join '; '). Execução bloqueada."
    }
    $existingContainers = @(& docker ps -aq --filter "label=com.docker.compose.project=$project")
    $existingNetworks = @(& docker network ls -q --filter "label=com.docker.compose.project=$project")
    $existingVolumes = @(& docker volume ls -q --filter "label=com.docker.compose.project=$project")
    if ($existingContainers -or $existingNetworks -or $existingVolumes) { throw "Nome aleatório já possui recursos Docker." }

    $imageMayExist = $true
    & docker compose --project-name $project --file $composeFile build app-image
    if ($LASTEXITCODE -ne 0) { throw "Imagem de teste Beta 9 não foi construída." }
    & docker compose --profile build-only --project-name $project --file $composeFile run --rm --no-deps app-image
    if ($LASTEXITCODE -ne 0) { throw "Testes offline do protocolo Beta 9 falharam." }
    & docker compose --project-name $project --file $composeFile up -d mongo
    if ($LASTEXITCODE -ne 0) { throw "MongoDB descartável Beta 9 não iniciou." }
    $resourcesMayExist = $true
    $containerId = (& docker compose --project-name $project --file $composeFile ps -q --no-trunc mongo).Trim()
    $networkId = (& docker network inspect $networkName --format '{{.Id}}').Trim()
    if ($LASTEXITCODE -ne 0 -or $containerId -notmatch '^[a-f0-9]{64}$' -or $networkId -notmatch '^[a-f0-9]{64}$') {
        throw "Identidades Docker incompletas; testes persistentes bloqueados."
    }
    Assert-OwnedMongo
    [Environment]::SetEnvironmentVariable("BETA8_3_DOCKER_PRECHECKED", "true", "Process")
    [Environment]::SetEnvironmentVariable("BETA8_3_DOCKER_CONTAINER_ID", $containerId, "Process")
    [Environment]::SetEnvironmentVariable("BETA8_3_DOCKER_NETWORK_ID", $networkId, "Process")
    Write-Output "Gate Beta 9 aprovado: banco, rede e armazenamento pertencem exclusivamente a esta execução."

    & docker compose --project-name $project --file $composeFile run --rm rs-init
    if ($LASTEXITCODE -ne 0) { throw "Replica set descartável não foi inicializado." }
    & docker compose --project-name $project --file $composeFile run --rm provisioner
    if ($LASTEXITCODE -ne 0) { throw "Provisionamento sintético falhou; cadeia persistente bloqueada." }
    & docker compose --project-name $project --file $composeFile up -d authority api
    if ($LASTEXITCODE -ne 0) { throw "API ou autoridade separada não iniciou." }
    $apiContainerId = (& docker compose --project-name $project --file $composeFile ps -q --no-trunc api).Trim()
    $authorityContainerId = (& docker compose --project-name $project --file $composeFile ps -q --no-trunc authority).Trim()
    if (
        $apiContainerId -notmatch '^[a-f0-9]{64}$' -or
        $authorityContainerId -notmatch '^[a-f0-9]{64}$' -or
        $apiContainerId -eq $authorityContainerId
    ) { throw "Processos/contêineres independentes não foram demonstrados." }
    $api = @(Invoke-DockerJson @("inspect", $apiContainerId))[0]
    $authority = @(Invoke-DockerJson @("inspect", $authorityContainerId))[0]
    if (
        $api.State.Pid -eq $authority.State.Pid -or
        $api.Config.Env -match 'BETA8_3_AUTHORITY_MONGO_URI|BETA8_3_AUTHORITY_PASSWORD|BETA8_3_ROOT_PASSWORD' -or
        $api.Config.Env -match 'BETA8_3_STAGE_(READ|WRITE)_URI|BETA8_3_STAGE_(READ|WRITE)_PASSWORD|BETA8_3_STAGER_SECRET_HEX' -or
        $authority.Config.Env -match 'BETA8_3_API_MONGO_URI|BETA8_3_API_PASSWORD|BETA8_3_ROOT_PASSWORD' -or
        $authority.Config.Env -match 'BETA8_3_STAGE_WRITE_URI|BETA8_3_STAGE_WRITE_PASSWORD' -or
        $api.Config.Env -notcontains "MONGO_URL=$apiUri" -or
        $authority.Config.Env -notcontains "MONGO_URL=$authorityUri"
    ) { throw "PIDs ou fronteira de ambiente divergem da composição de teste." }
    Assert-ProjectOwnership
    Write-Output "Processos separados confirmados; API PID $($api.State.Pid), autoridade PID $($authority.State.Pid); segredos omitidos."

    Invoke-AuthorityRestartVerifier

    $repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
    $snapshotOutput = & python (Join-Path $repositoryRoot "backend\test_support\beta9_curriculum_snapshot.py") `
        --repository $repositoryRoot --destination $sourceSnapshot
    if ($LASTEXITCODE -ne 0) { throw "Snapshot curricular Beta 9 não passou na verificação de proveniência." }
    Write-Output "Snapshot curricular validado: $snapshotOutput"

    & docker compose --project-name $project --file $composeFile up -d source-seeder
    if ($LASTEXITCODE -ne 0) { throw "Preparador de prévia descartável não iniciou." }
    $sourceSeederContainerId = (& docker compose --project-name $project --file $composeFile ps -q --no-trunc source-seeder).Trim()
    if ($sourceSeederContainerId -notmatch '^[a-f0-9]{64}$') { throw "Identidade do preparador Beta 9 inválida." }
    Assert-ProjectOwnership
    & docker exec $sourceSeederContainerId mkdir -p /tmp/beta9-source
    if ($LASTEXITCODE -ne 0) { throw "Destino temporário do preparador não ficou disponível." }
    # Windows PowerShell 5.1 text-decodes native stdout pipelines; use cmd's
    # byte-preserving pipe so the verified tar stream is not altered in transit.
    $snapshotCopyCommand = "tar -cf - -C `"$sourceSnapshot`" . | docker exec --interactive $sourceSeederContainerId tar -xf - -C /tmp/beta9-source"
    & cmd.exe /d /c $snapshotCopyCommand
    if ($LASTEXITCODE -ne 0) { throw "Cópia dos artefatos verificados para o contêiner próprio falhou." }
    $seedOutput = @(& docker exec $sourceSeederContainerId python /repo/backend/test_support/beta9_seed_fullstack_preview.py)
    if ($LASTEXITCODE -ne 0) { throw "Importação e preparação da prévia real Beta 9 falhou." }
    try { $fixture = $seedOutput[-1] | ConvertFrom-Json } catch { throw "Preparador Beta 9 não retornou o contrato esperado." }
    if (
        $fixture.batch_id -notmatch '^phase1-[0-9a-f]{64}$' -or
        $fixture.unit_count -ne 10 -or $fixture.module_count -ne 3 -or
        $fixture.source_revision -ne "migration@147dc68:tracked-clean-first-phase-files" -or
        $fixture.rubric_state -ne "PROPOSED" -or
        $fixture.private_track_id -notmatch '^[0-9a-f]{24}$'
    ) { throw "Fixture Beta 9 diverge da proveniência ou dos bloqueios pedagógicos esperados." }
    $environmentValues["BETA9_PREVIEW_BATCH_ID"] = [string]$fixture.batch_id
    $environmentValues["BETA9_PRIVATE_TRACK_ID"] = [string]$fixture.private_track_id
    [Environment]::SetEnvironmentVariable("BETA9_PREVIEW_BATCH_ID", $fixture.batch_id, "Process")
    [Environment]::SetEnvironmentVariable("BETA9_PRIVATE_TRACK_ID", $fixture.private_track_id, "Process")
    Write-Output "BETA9_REAL_CURRICULUM_PREVIEW: PASS; 3 módulos, 10 unidades, draft/private, rubrica PROPOSED."

    Assert-ProjectOwnership
    & docker compose --project-name $project --file $composeFile rm --stop --force source-seeder
    if ($LASTEXITCODE -ne 0) { throw "Contêiner privilegiado de preparação não foi removido." }
    $sourceSeederContainerId = ""
    & docker compose --project-name $project --file $composeFile up -d web
    if ($LASTEXITCODE -ne 0) { throw "Frontend de prévia Beta 9 não iniciou." }
    $webContainerId = (& docker compose --project-name $project --file $composeFile ps -q --no-trunc web).Trim()
    if ($webContainerId -notmatch '^[a-f0-9]{64}$') { throw "Identidade do frontend Beta 9 inválida." }
    Assert-ProjectOwnership
    $webReady = $false
    $webDeadline = [DateTime]::UtcNow.AddSeconds(90)
    while ([DateTime]::UtcNow -lt $webDeadline) {
        $webRunning = (& docker inspect $webContainerId --format '{{.State.Running}}').Trim()
        if ($LASTEXITCODE -ne 0 -or $webRunning -ne "true") { break }
        & docker exec $webContainerId node -e "fetch('http://127.0.0.1:3000').then(r=>process.exit(r.status<500?0:1)).catch(()=>process.exit(2))" | Out-Null
        if ($LASTEXITCODE -eq 0) { $webReady = $true; break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $webReady) {
        $webLogs = (& docker compose --project-name $project --file $composeFile logs --no-color web 2>&1) -join "`n"
        foreach ($entry in $environmentValues.GetEnumerator()) {
            if ($entry.Key -match "PASSWORD|SECRET|URI|TOKEN|KEY" -and $entry.Value) {
                $webLogs = $webLogs.Replace([string]$entry.Value, "[redacted]")
            }
        }
        Write-Output "Frontend startup diagnostics:"
        ($webLogs -split "`r?`n" | Select-Object -Last 30) | ForEach-Object { Write-Output $_ }
        throw "Frontend interno não ficou pronto antes do Playwright."
    }
    & docker compose --project-name $project --file $composeFile run --rm browser
    if ($LASTEXITCODE -ne 0) { throw "Jornada Playwright Beta 9 falhou na composição integrada." }
    Write-Output "BETA9_PLAYWRIGHT_REAL_CURRICULUM: PASS; frontend, API, autoridade, MongoDB e prévia com 10 unidades."
    Assert-ProjectOwnership
    $exitCode = 0
}
catch {
    Write-Error $_
    $exitCode = 1
}
finally {
    if ($resourcesMayExist) {
        try {
            Assert-ProjectOwnership
            & docker compose --project-name $project --file $composeFile down --remove-orphans
            if ($LASTEXITCODE -ne 0) { throw "Cleanup Compose Beta 9 falhou." }
            if (@(& docker ps -aq --filter "label=com.docker.compose.project=$project") -or
                @(& docker network ls -q --filter "label=com.docker.compose.project=$project") -or
                @(& docker volume ls -q --filter "label=com.docker.compose.project=$project")) {
                throw "Recursos Beta 9 permaneceram após a limpeza verificada."
            }
            Write-Output "Contêineres, rede e armazenamento temporário Beta 9 removidos após revalidação de propriedade."
        }
        catch {
            Write-Error $_
            $exitCode = 3
        }
    }
    if ($imageMayExist) {
        try { Remove-OwnedImage } catch { Write-Error $_; $exitCode = 3 }
    }
    if (Test-Path -LiteralPath $keyPath) { Remove-Item -LiteralPath $keyPath -Force }
    if (Test-Path -LiteralPath $sourceSnapshot) {
        $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\') + '\'
        $snapshotFullPath = [System.IO.Path]::GetFullPath($sourceSnapshot)
        $expectedSnapshotName = "trilhacode-beta9-source-$runId"
        if (
            -not $snapshotFullPath.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
            [System.IO.Path]::GetFileName($snapshotFullPath) -ne $expectedSnapshotName
        ) { throw "Propriedade do snapshot temporário não comprovada; dados preservados." }
        Remove-Item -LiteralPath $snapshotFullPath -Recurse -Force
    }
    foreach ($path in @($verifierStdout, $verifierStderr)) {
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
    }
    [Array]::Clear($keyBytes, 0, $keyBytes.Length)
    foreach ($name in $environmentValues.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], "Process")
    }
    foreach ($name in @("rootPassword", "apiPassword", "authorityPassword", "stageWritePassword", "stageReadPassword", "stageOwnerToken", "serviceSecret", "operationKey", "jwtSecret", "studentPassword", "reviewerPassword", "unscopedPassword", "adminPassword", "rootUri", "apiUri", "authorityUri", "stageWriteUri", "stageReadUri")) {
        Set-Variable -Name $name -Value $null -Scope Script
    }
    $environmentValues.Clear()
    $previousEnvironment.Clear()
}

exit $exitCode
