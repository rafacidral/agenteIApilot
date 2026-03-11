$user = 'testegpes'
$pass = 't3$tegpes'
$pair = "$($user):$($pass)"
$encodedCreds = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($pair))
$basicAuthValue = "Basic $encodedCreds"
$headers = @{
    Authorization = $basicAuthValue
}
$url = "http://teste458:9090/computer/api/json"
try {
    $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
    
    $onlineVMs = $response.computer | Where-Object { $_.offline -eq $false -and $_.displayName -ne 'Built-In Node' } | Select-Object displayName
    
    Write-Output "VMs Online:"
    $onlineVMs | Format-Table -AutoSize
} catch {
    Write-Error "Failed to fetch data from Jenkins API: $_"
}
