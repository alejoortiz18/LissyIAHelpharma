# E2E: Analista crea tipo de solicitud → Operario lo ve y registra evento
$ErrorActionPreference = 'Stop'
$BaseUrl = 'http://localhost:5002'
$Password = 'Yopmail2026'
$Analista = 'sofia.gomez@yopmail.com'
$Operario = 'prueba.operario@yopmail.com'
$suffix = Get-Date -Format 'yyyyMMddHHmmss'
$Codigo = "E2E_$suffix"
$Nombre = "Prueba E2E $suffix"

function Get-AntiforgeryToken {
    param([string]$Html)
    if ($Html -match 'name="__RequestVerificationToken"\s+(?:type="hidden"\s+)?value="([^"]+)"') { return $Matches[1] }
    if ($Html -match 'value="([^"]+)"\s+name="__RequestVerificationToken"') { return $Matches[1] }
    if ($Html -match "const TOKEN = '([^']+)'") { return $Matches[1] }
    if ($Html -match 'name="__RequestVerificationToken"\s+content="([^"]+)"') { return $Matches[1] }
    if ($Html -match 'content="([^"]+)"\s+name="__RequestVerificationToken"') { return $Matches[1] }
    if ($Html -match "return input \? input\.value : '([^']+)'") { return $Matches[1] }
    throw 'No se encontró token antiforgery'
}

function Wait-AppReady {
    param([int]$MaxSec = 60)
    $deadline = (Get-Date).AddSeconds($MaxSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest -Uri "$BaseUrl/Cuenta/Login" -UseBasicParsing -TimeoutSec 3
            if ($r.StatusCode -eq 200) { return }
        } catch { Start-Sleep -Seconds 2 }
    }
    throw "La app no respondió en $BaseUrl tras ${MaxSec}s"
}

function Invoke-WebSessionLogin {
    param([string]$Correo, [string]$Pwd)
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $loginPage = Invoke-WebRequest -Uri "$BaseUrl/Cuenta/Login" -WebSession $session -UseBasicParsing
    $token = Get-AntiforgeryToken $loginPage.Content
    $body = @{
        CorreoAcceso = $Correo
        Password = $Pwd
        __RequestVerificationToken = $token
    }
    $resp = Invoke-WebRequest -Uri "$BaseUrl/Cuenta/Login" -Method POST -WebSession $session -Body $body -UseBasicParsing -MaximumRedirection 5
    if ($resp.BaseResponse.ResponseUri.AbsolutePath -match '/Cuenta/Login') {
        throw "Login fallido para $Correo (revisa contraseña o usuario en BD)."
    }
    return $session
}

function Post-FormAjax {
    param(
        [Microsoft.PowerShell.Commands.WebRequestSession]$Session,
        [string]$Url,
        [hashtable]$Fields,
        [string]$PageUrl
    )
    $page = Invoke-WebRequest -Uri $PageUrl -WebSession $Session -UseBasicParsing
    $token = Get-AntiforgeryToken $page.Content
    $parts = @("__RequestVerificationToken=$([uri]::EscapeDataString($token))")
    foreach ($k in $Fields.Keys) {
        $v = $Fields[$k]
        if ($null -ne $v) { $parts += "$k=$([uri]::EscapeDataString("$v"))" }
    }
    $body = $parts -join '&'
    $headers = @{ 'RequestVerificationToken' = $token }
    return Invoke-WebRequest -Uri $Url -Method POST -WebSession $Session `
        -ContentType 'application/x-www-form-urlencoded' -Body $body -Headers $headers -UseBasicParsing
}

Write-Host "Esperando aplicación en $BaseUrl..." -ForegroundColor Cyan
Wait-AppReady

Write-Host "`n=== 1. Analista: crear tipo '$Nombre' (código $Codigo) ===" -ForegroundColor Yellow
$sAn = Invoke-WebSessionLogin $Analista $Password
$crear = Post-FormAjax -Session $sAn `
    -Url "$BaseUrl/Catalogos/CrearTipoSolicitudAjax" `
    -PageUrl "$BaseUrl/Catalogos/Index?tab=tipos-solicitud" `
    -Fields @{ Nombre = $Nombre; Codigo = $Codigo; EsVacaciones = 'false' }
if ($crear.Content -notmatch '"exito"\s*:\s*true') {
    Write-Host "Respuesta crear tipo: $($crear.Content)" -ForegroundColor Red
    throw 'No se pudo crear el tipo de solicitud'
}
Write-Host "[OK] Tipo creado en Maestros" -ForegroundColor Green

Write-Host "`n=== 2. Operario: tipo visible en modal Registrar evento ===" -ForegroundColor Yellow
$sOp = Invoke-WebSessionLogin $Operario $Password
$eventos = Invoke-WebRequest -Uri "$BaseUrl/EventoLaboral/Index" -WebSession $sOp -UseBasicParsing
if ($eventos.Content -notlike "*value=`"$Codigo`"*") {
    Write-Host "[FAIL] El código $Codigo no aparece en el select #ev-tipo" -ForegroundColor Red
    exit 1
}
if ($eventos.Content -notlike "*$Nombre*") {
    Write-Host "[FAIL] El nombre '$Nombre' no aparece en la página de eventos" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Tipo visible en formulario de registro" -ForegroundColor Green

Write-Host "`n=== 3. Operario: registrar evento con el nuevo tipo ===" -ForegroundColor Yellow
$empIdLine = sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -h -1 -W -Q "SET NOCOUNT ON; SELECT e.Id FROM dbo.Empleados e INNER JOIN dbo.Usuarios u ON e.UsuarioId=u.Id WHERE u.CorreoAcceso=N'$Operario'"
$empId = [int]($empIdLine | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)
if (-not $empId) { throw "No se encontró EmpleadoId para $Operario" }

$inicio = (Get-Date).AddDays(120).ToString('yyyy-MM-dd')
$fin    = (Get-Date).AddDays(124).ToString('yyyy-MM-dd')

$reg = Post-FormAjax -Session $sOp `
    -Url "$BaseUrl/EventoLaboral/RegistrarAjax" `
    -PageUrl "$BaseUrl/EventoLaboral/Index" `
    -Fields @{
        EmpleadoId    = $empId
        TipoEvento    = $Codigo
        FechaInicio   = $inicio
        FechaFin      = $fin
        AutorizadoPor = 'Supervisor E2E'
        Descripcion   = "Evento de prueba tipo $Codigo"
    }
if ($reg.Content -notmatch '"exito"\s*:\s*true') {
    Write-Host "Respuesta registrar: $($reg.Content)" -ForegroundColor Red
    throw 'No se pudo registrar el evento'
}
Write-Host "[OK] Evento registrado ($inicio → $fin)" -ForegroundColor Green

Write-Host "`n=== 4. Operario: tipo aparece en listado ===" -ForegroundColor Yellow
$list = Invoke-WebRequest -Uri "$BaseUrl/EventoLaboral/Index" -WebSession $sOp -UseBasicParsing
if ($list.Content -notlike "*$Nombre*" -and $list.Content -notlike "*$Codigo*") {
    Write-Host "[FAIL] El evento no aparece en la grilla con tipo '$Nombre'" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Listado muestra el nuevo tipo de evento" -ForegroundColor Green

Write-Host "`n=== PRUEBA COMPLETADA ===" -ForegroundColor Green
Write-Host "Tipo: $Nombre ($Codigo)" -ForegroundColor Cyan
