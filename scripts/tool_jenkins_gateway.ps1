<#
.SYNOPSIS
    Gateway centralizado de chamadas à API do Jenkins para o Agente IA Pilot.

.DESCRIPTION
    A IA deve obrigatoriamente passar um parâmetro -Acao válido.
    Ações permitidas: status_vms | versao_jenkins | falhas_ultima_execucao
    Qualquer outro valor retorna um bloqueio estruturado em JSON.

.PARAMETER Acao
    Tag da operação a executar. Deve ser uma das ações autorizadas.

.EXAMPLE
    .\tool_jenkins_gateway.ps1 -Acao status_vms
#>
param (
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Acao
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ==========================================
# CREDENCIAIS DE ACESSO
# ==========================================
$user    = 'testegpes'
$pass    = 't3$tegpes'  # Aspas simples: o $ não é avaliado pelo PowerShell
$pair    = "$($user):$($pass)"
$encoded = [System.Convert]::ToBase64String(
    [System.Text.Encoding]::ASCII.GetBytes($pair)
)
$headers = @{ Authorization = "Basic $encoded" }
$baseUrl = "http://teste458:9090"

# Helper: serializa um hashtable e imprime a linha de resultado
function Write-Resultado {
    param([hashtable]$Dados)
    $json = ConvertTo-Json -InputObject $Dados -Compress
    Write-Output "RESULTADO_JSON_PARA_IA: $json"
}

Write-Host "[INFO] Gateway chamado com acao='$Acao'" -ForegroundColor Cyan

# ==========================================
# ROTEADOR DE AÇÕES
# ==========================================
switch ($Acao.ToLower()) {

    "status_vms" {
        $url      = "$baseUrl/computer/api/json"
        $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
        
        $todos   = $response.computer | Where-Object { $_.displayName -ne 'Built-In Node' }
        $online  = ($todos | Where-Object { $_.offline -eq $false }).displayName
        $offline = ($todos | Where-Object { $_.offline -eq $true  }).displayName

        Write-Resultado @{
            vms_online  = @($online)
            vms_offline = @($offline)
            total_online = @($online).Count
        }
    }

    "versao_jenkins" {
        # A versão não vem no corpo JSON — está no header HTTP X-Jenkins
        $response = Invoke-WebRequest -Uri "$baseUrl/api/json" -Method Get -Headers $headers -UseBasicParsing
        $versao   = $response.Headers["X-Jenkins"]

        if (-not $versao) {
            Write-Resultado @{ erro = "Header X-Jenkins não encontrado na resposta." }
        } else {
            Write-Resultado @{ versao_jenkins = $versao }
        }
    }

    "falhas_ultima_execucao" {
        $url = "$baseUrl/job/6-executar-testes/lastBuild/api/json" +
               "?tree=result,timestamp,duration,builtOn,number"

        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
            Write-Resultado @{
                numero         = $response.number
                status         = $response.result
                duracao_ms     = $response.duration
                executado_em   = $response.builtOn
                timestamp_unix = $response.timestamp
            }
        } catch {
            Write-Resultado @{
                erro = "Não foi possível obter o último build: $($_.Exception.Message)"
            }
        }
    }

    "total_jobs" {
        $url = "$baseUrl/api/json?tree=jobs[name]"
        
        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers -UseBasicParsing
            $qtd = 0
            if ($response.jobs) {
                $qtd = @($response.jobs).Count
            }
            Write-Resultado @{ total_jobs = $qtd }
        } catch {
            Write-Resultado @{ erro = "Falha ao contar jobs: $($_.Exception.Message)" }
        }
    }

    default {
        # BLOQUEIO DE ANSIEDADE — ação inventada pela IA
        Write-Host "[BLOQUEIO] Acao nao mapeada recebida: '$Acao'" -ForegroundColor Red
        Write-Resultado @{
            erro = ("ACAO_NAO_MAPEADA. O gateway nao tem suporte para '$Acao'. " +
                    "Diga ao usuario: 'Chefe, nao tenho um comando mapeado para isso ainda. " +
                    "As acoes disponiveis sao: status_vms, versao_jenkins, falhas_ultima_execucao.'")
        }
    }
}
