param(
    [string]$SourceRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'Sprite\Sprite de Holy Knight'),
    [string]$OutputRoot = (Join-Path $PSScriptRoot 'adapted-sprites\holy')
)
$ErrorActionPreference = 'Stop'
$converter = Join-Path $PSScriptRoot 'sprite-converter\bin\Release\net9.0-windows\SpriteConverter.dll'
foreach ($variant in @(@('HolyKnight Male.BMP','black'), @('HolyKnight Female.bmp','blue'))) {
    & dotnet $converter --prepare-holy (Join-Path $SourceRoot $variant[0]) (Join-Path $OutputRoot $variant[0]) $variant[1]
    if ($LASTEXITCODE -ne 0) { throw "Sprite preparation failed: $($variant[0])" }
}
Copy-Item -LiteralPath (Join-Path $SourceRoot 'Icon Holy Knight.jfif') -Destination $OutputRoot -Force
