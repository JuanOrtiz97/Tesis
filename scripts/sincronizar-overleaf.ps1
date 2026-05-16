param(
  [string]$Mensaje = "Actualizar tesis"
)

$ErrorActionPreference = "Stop"

$root = git rev-parse --show-toplevel
Set-Location $root

$branch = git branch --show-current
if (-not $branch) {
  throw "No se pudo detectar la rama actual."
}

git add -A

$hasChanges = git status --porcelain
if ($hasChanges) {
  git commit -m $Mensaje
} else {
  Write-Host "No hay cambios para commitear."
}

Write-Host "Enviando cambios a GitHub..."
git push origin $branch

$overleafRemote = git remote | Where-Object { $_ -eq "overleaf" }
if ($overleafRemote) {
  Write-Host "Enviando cambios a Overleaf..."
  git push overleaf HEAD:master
} else {
  Write-Host "Falta configurar el remoto de Overleaf."
  Write-Host "Ejecuta: git remote add overleaf https://git.overleaf.com/ID_DEL_PROYECTO"
  Write-Host "Luego vuelve a correr: .\scripts\sincronizar-overleaf.ps1"
}
