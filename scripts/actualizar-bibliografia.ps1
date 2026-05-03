$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$output = Join-Path $repoRoot "bibliografia\Maestria.bib"
$url = "http://127.0.0.1:23119/better-bibtex/export?/library;id:1/collection;key:DLNGGFAR/Maestria.biblatex"

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $output) | Out-Null
curl.exe -L -o $output $url

$text = Get-Content -Raw -Encoding UTF8 -LiteralPath $output
$text = [regex]::Replace($text, '(?ms)^\s*(file|abstract)\s*=\s*\{(?:[^{}]|\{[^{}]*\})*\},?\r?\n', '')
Set-Content -LiteralPath $output -Value $text -Encoding UTF8

Write-Host "Bibliografia actualizada en $output"
