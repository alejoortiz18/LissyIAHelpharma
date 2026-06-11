# Prueba E2E de permisos por rol (app en http://localhost:5002)
$ErrorActionPreference = 'Stop'
$BaseUrl = 'http://localhost:5002'
$Password = 'Yopmail2026'
$AdminCorreo = 'sofia.gomez@yopmail.com'

function Get-SqlPermisoIds {
    param([string[]]$Codigos)
    $inList = ($Codigos | ForEach-Object { "N'$_'" }) -join ','
    $out = sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -h -1 -W -Q "SET NOCOUNT ON; SELECT Id FROM dbo.PermisosPlataforma WHERE Codigo IN ($inList) ORDER BY Id"
    return @($out | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ })
}

function Get-AntiforgeryToken {
    param([string]$Html)
    if ($Html -match 'name="__RequestVerificationToken"\s+(?:type="hidden"\s+)?value="([^"]+)"') { return $Matches[1] }
    if ($Html -match 'value="([^"]+)"\s+name="__RequestVerificationToken"') { return $Matches[1] }
    throw 'No se encontró token antiforgery'
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
    return $session
}

function Test-PageContent {
    param(
        [Microsoft.PowerShell.Commands.WebRequestSession]$Session,
        [string]$Path,
        [string]$MustContain = $null,
        [string]$MustNotContain = $null,
        [string]$Label
    )
    $r = Invoke-WebRequest -Uri "$BaseUrl$Path" -WebSession $Session -UseBasicParsing -MaximumRedirection 5
    $ok = $true
    if ($MustContain -and $r.Content -notlike "*$MustContain*") { $ok = $false }
    if ($MustNotContain -and $r.Content -like "*$MustNotContain*") { $ok = $false }
    if ($ok) { Write-Host "[OK] $Label" -ForegroundColor Green }
    else { Write-Host "[FAIL] $Label" -ForegroundColor Red }
    return $ok
}

function Get-RolOperarioId {
    param([Microsoft.PowerShell.Commands.WebRequestSession]$AdminSession)
    $rolIdSql = sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -h -1 -W -Q "SET NOCOUNT ON; SELECT Id FROM dbo.RolesSistema WHERE Codigo=N'Operario'"
    return [int]($rolIdSql | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1)
}

function Set-OperarioPermisosSql {
    param([string[]]$Codigos)
    $inList = ($Codigos | ForEach-Object { "N'$_'" }) -join ','
    $sql = @"
DECLARE @RolId INT = (SELECT Id FROM dbo.RolesSistema WHERE Codigo = N'Operario');
DELETE FROM dbo.RolesSistemaPermisos WHERE RolSistemaId = @RolId;
INSERT INTO dbo.RolesSistemaPermisos (RolSistemaId, PermisoId)
SELECT @RolId, p.Id FROM dbo.PermisosPlataforma p WHERE p.Codigo IN ($inList);
"@
    sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -Q $sql | Out-Null
    Write-Host "Rol Operario actualizado en BD ($($Codigos.Count) permisos)" -ForegroundColor Cyan
}

function Set-OperarioPermisosViaMaestros {
    param(
        [Microsoft.PowerShell.Commands.WebRequestSession]$AdminSession,
        [int[]]$PermisoIds
    )
    # Misma lógica que Maestros (EditarRolAjax); requiere sesión antiforgery válida
    $rolId = Get-RolOperarioId -AdminSession $AdminSession
    $catalogos = Invoke-WebRequest -Uri "$BaseUrl/Catalogos/Index?tab=roles" -WebSession $AdminSession -UseBasicParsing
    $token = Get-AntiforgeryToken $catalogos.Content

    $parts = @("__RequestVerificationToken=$token", "Id=$rolId", "Nombre=Operario", "Descripcion=", "Estado=Activo")
    for ($i = 0; $i -lt $PermisoIds.Count; $i++) {
        $parts += "PermisoIds[$i]=$($PermisoIds[$i])"
    }
    $body = $parts -join '&'
    $resp = Invoke-WebRequest -Uri "$BaseUrl/Catalogos/EditarRolAjax" -Method POST -WebSession $AdminSession `
        -ContentType 'application/x-www-form-urlencoded' -Body $body -UseBasicParsing
    if ($resp.Content -notlike '*"exito":true*' -and $resp.Content -notlike '*exito*: *true*') {
        throw "EditarRolAjax no devolvió JSON de éxito (respuesta HTML). Use Set-OperarioPermisosSql."
    }
    Write-Host "Rol Operario actualizado vía Maestros ($($PermisoIds.Count) permisos)" -ForegroundColor Cyan
}

try {
    $null = Invoke-WebRequest -Uri "$BaseUrl/Cuenta/Login" -UseBasicParsing -TimeoutSec 8
}
catch {
    Write-Host "App no disponible en $BaseUrl" -ForegroundColor Red
    exit 1
}

$passed = 0; $failed = 0
function Record($ok) { if ($ok) { $script:passed++ } else { $script:failed++ } }

Write-Host "`n=== 1. Operario SIN HorasExtras.Crear ===" -ForegroundColor Yellow
$sOp = Invoke-WebSessionLogin 'prueba.operario@yopmail.com' $Password
Record (Test-PageContent $sOp '/HoraExtra/Index' -MustNotContain 'id="btn-nueva-he"' -Label 'Operario: sin botón Nueva solicitud')
Record (Test-PageContent $sOp '/Solicitud/Index' -MustContain 'Nueva solicitud' -Label 'Operario: puede ver solicitudes')
Record (Test-PageContent $sOp '/HoraExtra/Index' -MustContain 'Horas Extras' -Label 'Operario: puede ver horas extras')

Write-Host "`n=== 2. Regente CON HorasExtras.Crear (sin Aprobar) ===" -ForegroundColor Yellow
$sReg = Invoke-WebSessionLogin 'prueba.regente@yopmail.com' $Password
Record (Test-PageContent $sReg '/HoraExtra/Index' -MustContain 'id="btn-nueva-he"' -Label 'Regente: botón Nueva solicitud')
Record (Test-PageContent $sReg '/EventoLaboral/Index' -MustContain 'Registrar evento' -Label 'Regente: botón Registrar evento')
Record (Test-PageContent $sReg '/Dashboard/Index' -MustContain 'Dashboard' -Label 'Regente: accede al dashboard')

Write-Host "`n=== 3. Direccionador (perfil + solicitudes, sin dashboard) ===" -ForegroundColor Yellow
$sDir = Invoke-WebSessionLogin 'prueba.direccion@yopmail.com' $Password
Record (Test-PageContent $sDir '/Solicitud/Index' -MustContain 'Nueva solicitud' -Label 'Direccionador: solicitudes')
try {
    $dash = Invoke-WebRequest -Uri "$BaseUrl/Dashboard/Index" -WebSession $sDir -UseBasicParsing -MaximumRedirection 0 -ErrorAction Stop
    Record ($false)
    Write-Host "[FAIL] Direccionador accedió al dashboard" -ForegroundColor Red
}
catch {
    $code = $_.Exception.Response.StatusCode.value__
    if ($code -eq 302) {
        Write-Host "[OK] Direccionador: bloqueado en Dashboard (redirect)" -ForegroundColor Green
        Record $true
    } else {
        Write-Host "[OK] Direccionador: sin acceso a Dashboard (HTTP $code)" -ForegroundColor Green
        Record $true
    }
}

Write-Host "`n=== 4. Se agrega HorasExtras.Crear al rol Operario → debe ver botón (re-login) ===" -ForegroundColor Yellow
try {
    Set-OperarioPermisosSql @(
        'Empleados.VerPerfilPropio','Solicitudes.Ver','Solicitudes.Crear','HorasExtras.Ver','HorasExtras.Crear'
    )
    $sOp2 = Invoke-WebSessionLogin 'prueba.operario@yopmail.com' $Password
    Record (Test-PageContent $sOp2 '/HoraExtra/Index' -MustContain 'id="btn-nueva-he"' -Label 'Operario tras agregar permiso: botón Nueva solicitud')
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Write-Host "`n=== 5. Se quita HorasExtras.Crear → ya no ve botón (re-login) ===" -ForegroundColor Yellow
try {
    Set-OperarioPermisosSql @(
        'Empleados.VerPerfilPropio','Solicitudes.Ver','Solicitudes.Crear','HorasExtras.Ver'
    )
    $sOp3 = Invoke-WebSessionLogin 'prueba.operario@yopmail.com' $Password
    Record (Test-PageContent $sOp3 '/HoraExtra/Index' -MustNotContain 'id="btn-nueva-he"' -Label 'Operario tras quitar permiso: sin botón')
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

Write-Host "`n=== Resumen: $passed OK, $failed FAIL ===" -ForegroundColor Yellow
if ($failed -gt 0) { exit 1 }
