$user = 'testegpes'
$pass = 't3$tegpes'
$pair = "$($user):$($pass)"
$encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))
$basicAuthValue = "Basic $encodedCreds"
$headers = @{
    Authorization = $basicAuthValue
}

# 1. Obter VMs Online
$urlNodes = "http://teste458:9090/computer/api/json"
$responseNodes = Invoke-RestMethod -Uri $urlNodes -Headers $headers -Method Get
$onlineVMs = $responseNodes.computer | Where-Object { $_.offline -eq $false -and $_.displayName -ne 'Built-In Node' } | Select-Object -ExpandProperty displayName
# test458 is also considered an online master, let's include it if needed or follow what the first script gave (it included test458 but Built-In Node is what it is actually called in Jenkins, or test458 itself). Let's just keep the online array:
$validNodes = @("VWT001SATMHC003", "VWT001SATMHC005", "VWT001SATMHC006", "VWT001SATMHC007", "VWT001SATMHC008", "VWT001SATMHC009", "VWT001SATMHC010", "VWT001SATMHC011", "VWT001SATMHC012", "VWT001SATMHC013", "VWT001SATMHC014", "VWT001SATMHC015", "teste458", "Built-In Node")

Write-Host "--- Memoria de Calculo ---"
Write-Host "VMs Online Identificadas:"
$onlineVMs | ForEach-Object { Write-Host "- $_" }
Write-Host ""

# 2. Obter Builds do Job 6-executar-testes
$urlJob = "http://teste458:9090/job/6-executar-testes/api/json?tree=builds[number,duration,builtOn]"
$responseJob = Invoke-RestMethod -Uri $urlJob -Headers $headers -Method Get

# 3. Filtrar e Calcular
$builds = $responseJob.builds
$validBuilds = @()
$totalDurationMs = 0

foreach ($build in $builds) {
    if ($build.duration -gt 0 -and $onlineVMs -contains $build.builtOn) {
        $validBuilds += $build
        $totalDurationMs += $build.duration
    }
}

$qtdBuilds = $validBuilds.Count

Write-Host "Encontrados $qtdBuilds builds concluidos nas VMs online."

if ($qtdBuilds -gt 0) {
    $totalSeconds = $totalDurationMs / 1000
    $totalMinutes = $totalSeconds / 60
    $avgSeconds = $totalSeconds / $qtdBuilds
    $avgMinutes = $avgSeconds / 60
    
    Write-Host "Tempo total de execucao somado nas VMs online: $([math]::Round($totalMinutes, 2)) minutos ($([math]::Round($totalSeconds, 2)) segundos)."
    Write-Host "Tempo medio de execucao (Total / Numero de builds nas VMs online): $([math]::Round($avgMinutes, 2)) minutos ($([math]::Round($avgSeconds, 2)) segundos)."
} else {
    Write-Host "Nenhum build encontrado nas VMs online com duracao valida."
}

Write-Host "--- Fim da Memoria de Calculo ---"
