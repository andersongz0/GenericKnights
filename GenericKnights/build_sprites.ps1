param(
    [string]$ProjectRoot = $PSScriptRoot,
    [string]$GenericJobsRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'Nexus Mods\Generic Jobs\Mod Generic Jobs'),
    [string]$HolySpriteRoot = '',
    [string]$RuneSpriteRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'Sprite\Sprite de Rune Knight'),
    [string]$FF16Tools = (Join-Path (Split-Path $PSScriptRoot -Parent) 'FF16 Tools\win-x64\FF16Tools.CLI.exe'),
    [string]$ModOutputRoot = '',
    [string]$IconRoot = '',
    [string]$NativeSprRoot = '',
    [int]$HolyMalePortraitY = 256
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($HolySpriteRoot)) {
    $reviewedArt = Join-Path $ProjectRoot 'art-assets\holy'
    $HolySpriteRoot = if (Test-Path -LiteralPath (Join-Path $reviewedArt 'HolyKnight Male.BMP')) {
        $reviewedArt
    } else { Join-Path (Split-Path $ProjectRoot -Parent) 'Sprite\Sprite de Holy Knight' }
}
if (-not $PSBoundParameters.ContainsKey('HolyMalePortraitY') -and
    (Test-Path -LiteralPath (Join-Path $HolySpriteRoot 'HolyKnight Male.adaptation.json'))) {
    $HolyMalePortraitY = 456
}
Add-Type -AssemblyName System.Drawing
# Binary texture-parts records contain bytes above 0x7F. ASCII round-trips
# silently replace them with '?', corrupting coordinates and record offsets.
$partsEncoding = [Text.Encoding]::GetEncoding(28591)

$modRoot = if ([string]::IsNullOrWhiteSpace($ModOutputRoot)) { Join-Path $ProjectRoot 'Mod' } else { [IO.Path]::GetFullPath($ModOutputRoot) }
$g2dRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\system\ffto\g2d'
$faceTextureRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\ui\ffto\common\face\texture'
$facePartsRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\ui\ffto\common\face\textureparts'
$jobVisualTextureRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\ui\ffto\icon\job_visual\texture'
$jobVisualPartsRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\ui\ffto\icon\job_visual\textureparts'
$jobIconTextureRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\ui\ffto\icon\job\texture'
$jobIconPartsRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\ui\ffto\icon\job\textureparts'
$faceBuildRoot = Join-Path $ProjectRoot 'face-build'
$jobVisualBuildRoot = Join-Path $ProjectRoot 'jobvisual-build'
$spriteConverterProject = Join-Path $ProjectRoot 'sprite-converter\SpriteConverter.csproj'
$visualResourceRoot = Join-Path $modRoot 'Visuals'
New-Item -ItemType Directory -Force -Path $visualResourceRoot | Out-Null
& dotnet build $spriteConverterProject -c Release --nologo | Out-Host
if ($LASTEXITCODE -ne 0) { throw 'SPR converter build failed.' }
$spriteConverterDll = Join-Path $ProjectRoot 'sprite-converter\bin\Release\net9.0-windows\SpriteConverter.dll'
# The replacement Holy drawings are PNGs named .BMP. Adapt them without
# overwriting sources; their portrait strip is at the bottom, not row 256.
$holyHeader = [IO.File]::ReadAllBytes((Join-Path $HolySpriteRoot 'HolyKnight Male.BMP'))
if ($holyHeader[0] -eq 0x89 -and $holyHeader[1] -eq 0x50) {
    $adapted = Join-Path $ProjectRoot 'adapted-sprites\holy'
    & (Join-Path $ProjectRoot 'prepare_holy_sprites.ps1') -SourceRoot $HolySpriteRoot -OutputRoot $adapted
    $HolySpriteRoot = $adapted
    $HolyMalePortraitY = 456
}
New-Item -ItemType Directory -Force -Path $g2dRoot, $faceTextureRoot, $facePartsRoot, $jobVisualTextureRoot, $jobVisualPartsRoot, $jobIconTextureRoot, $jobIconPartsRoot, $faceBuildRoot | Out-Null
New-Item -ItemType Directory -Force -Path $jobVisualBuildRoot | Out-Null

# 1110..1130 are not extension slots.  They are allocated to Dark/Onion
# Knight and named WotL characters (Balthier, Luso, Argath and Aliste).  Do
# not ship replacement G2D pages here: it creates conflicts with GenericJobs
# and cannot change the native A2/A3 visual route.  The supplied sheets are
# registered through FFTModLoader.visuals.json instead of replacing these pages.
1118..1126 | ForEach-Object {
    $stale = Join-Path $g2dRoot "tex_$_.bin"
    if (Test-Path -LiteralPath $stale) { Remove-Item -LiteralPath $stale -Force }
}

# Never replace named unit_psp containers. The old native A2/A3 calculation
# overflows to shapes 16..19; replacing assets cannot fix that calculation.
$unitPspRoot = Join-Path $modRoot 'FFTIVC\data\enhanced\fftpack\unit_psp'
@(
    'spr_dst_bchr_valuhurea_m_spr.bin',
    'spr_dst_bchr_kaito_m_spr.bin',
    'spr_dst_bchr_algakuma_m_spr.bin',
    'spr_dst_bchr_arles_m_spr.bin'
) | ForEach-Object {
    $stale = Join-Path $unitPspRoot $_
    if (Test-Path -LiteralPath $stale) { Remove-Item -LiteralPath $stale -Force }
}

function Copy-G2dPair([int]$sourceTop, [int]$targetTop) {
    $sourceRoot = Join-Path $GenericJobsRoot 'FFTIVC\data\enhanced\system\ffto\g2d'
    Copy-Item -LiteralPath (Join-Path $sourceRoot "tex_$sourceTop.bin") -Destination (Join-Path $g2dRoot "tex_$targetTop.bin") -Force
    Copy-Item -LiteralPath (Join-Path $sourceRoot "tex_$($sourceTop + 1).bin") -Destination (Join-Path $g2dRoot "tex_$($targetTop + 1).bin") -Force
}

function Read-IndexedBmp([string]$path, [int]$portraitY = 456) {
    $bitmap = [System.Drawing.Bitmap]::new($path)
    if ($bitmap.PixelFormat -ne [System.Drawing.Imaging.PixelFormat]::Format8bppIndexed) {
        $bitmap.Dispose()
        throw "Expected an indexed 8bpp BMP: $path"
    }
    $rect = [System.Drawing.Rectangle]::new(0, 0, $bitmap.Width, $bitmap.Height)
    $data = $bitmap.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, $bitmap.PixelFormat)
    try {
        $stride = [Math]::Abs($data.Stride)
        $raw = New-Object byte[] ($stride * $bitmap.Height)
        [Runtime.InteropServices.Marshal]::Copy($data.Scan0, $raw, 0, $raw.Length)
        $indices = New-Object 'byte[,]' $bitmap.Height, $bitmap.Width
        for ($y = 0; $y -lt $bitmap.Height; $y++) {
            for ($x = 0; $x -lt $bitmap.Width; $x++) { $indices[$y, $x] = $raw[$y * $stride + $x] }
        }
        $palette = @($bitmap.Palette.Entries)
    } finally {
        $bitmap.UnlockBits($data)
        $bitmap.Dispose()
    }
    if ($portraitY -eq 256) {
        $normalized = New-Object 'byte[,]' 488, 256
        for ($y = 0; $y -lt 488; $y++) {
            $srcY = if ($y -lt 256) { $y } elseif ($y -lt 456) { $y + 32 } else { $y - 200 }
            for ($x = 0; $x -lt 256; $x++) { $normalized[$y, $x] = $indices[$srcY, $x] }
        }
        $indices = $normalized
    }
    return @{ Width = 256; Height = 488; Indices = $indices; Palette = $palette }
}

function Write-G2dSheet($sprite, [int]$sourceY, [string]$path) {
    $bytes = New-Object byte[] 131072
    $out = 0
    for ($y = 0; $y -lt 256; $y++) {
        $srcY = $sourceY + $y
        for ($repeatY = 0; $repeatY -lt 2; $repeatY++) {
            for ($x = 0; $x -lt 256; $x++) {
                $index = 0
                if ($srcY -lt $sprite.Height) { $index = $sprite.Indices[$srcY, $x] -band 0x0F }
                $bytes[$out++] = [byte]($index -bor ($index -shl 4))
            }
        }
    }
    [IO.File]::WriteAllBytes($path, $bytes)
}

function To-Rgb555([System.Drawing.Color]$color) {
    # Color channels are bytes. PowerShell preserves the left operand's type
    # during shifts, truncating the green/blue bits unless promoted first.
    return [uint16]((([int]$color.B -shr 3) -shl 10) -bor (([int]$color.G -shr 3) -shl 5) -bor ([int]$color.R -shr 3))
}

function Write-SprPalette([string]$path, [System.Drawing.Color[]]$battle, [System.Drawing.Color[]]$portrait) {
    $bytes = New-Object byte[] 45056
    for ($slot = 0; $slot -lt 16; $slot++) {
        $colors = if ($slot -lt 8) { $battle } else { $portrait }
        for ($i = 0; $i -lt 16; $i++) {
            $value = To-Rgb555 $colors[$i]
            $offset = $slot * 32 + $i * 2
            $bytes[$offset] = [byte]($value -band 0xFF)
            $bytes[$offset + 1] = [byte](($value -shr 8) -band 0xFF)
        }
    }
    [IO.File]::WriteAllBytes($path, $bytes)
}

function Update-SprPalette([string]$path, [System.Drawing.Color[]]$battle, [System.Drawing.Color[]]$portrait) {
    $bytes = [IO.File]::ReadAllBytes($path)
    if ($bytes.Length -lt 512) { throw "Invalid SPR container: $path" }
    for ($slot = 0; $slot -lt 16; $slot++) {
        $colors = if ($slot -lt 8) { $battle } else { $portrait }
        for ($i = 0; $i -lt 16; $i++) {
            $value = To-Rgb555 $colors[$i]
            $offset = $slot * 32 + $i * 2
            $bytes[$offset] = [byte]($value -band 0xFF)
            $bytes[$offset + 1] = [byte](($value -shr 8) -band 0xFF)
        }
    }
    [IO.File]::WriteAllBytes($path, $bytes)
}

function Get-PaletteRange($sprite, [int]$start) {
    [System.Drawing.Color[]]$colors = 0..15 | ForEach-Object { $sprite.Palette[$start + $_] }
    $colors[0] = [System.Drawing.Color]::FromArgb(0, 0, 0, 0)
    return $colors
}

function Write-RuneVariant([string]$bmpPath, [int]$topId, [string]$sprName) {
    $sprite = Read-IndexedBmp $bmpPath
    Write-G2dSheet $sprite 0 (Join-Path $g2dRoot "tex_$topId.bin")
    Write-G2dSheet $sprite 256 (Join-Path $g2dRoot "tex_$($topId + 1).bin")
    Write-SprPalette (Join-Path $unitPspRoot $sprName) (Get-PaletteRange $sprite 0) (Get-PaletteRange $sprite 128)
}

function Get-HolyPalette([string]$accent) {
    $common = @(
        [Drawing.Color]::FromArgb(0,0,0,0), [Drawing.Color]::FromArgb(255,16,18,24),
        [Drawing.Color]::FromArgb(255,40,45,56), [Drawing.Color]::FromArgb(255,73,79,92),
        [Drawing.Color]::FromArgb(255,112,119,132), [Drawing.Color]::FromArgb(255,160,166,178),
        [Drawing.Color]::FromArgb(255,205,210,219), [Drawing.Color]::FromArgb(255,245,247,250)
    )
    $accentColors = if ($accent -eq 'blue') {
        @([Drawing.Color]::FromArgb(255,11,45,83), [Drawing.Color]::FromArgb(255,20,82,145), [Drawing.Color]::FromArgb(255,42,133,208), [Drawing.Color]::FromArgb(255,104,186,242))
    } else {
        @([Drawing.Color]::FromArgb(255,86,24,61), [Drawing.Color]::FromArgb(255,151,48,105), [Drawing.Color]::FromArgb(255,215,92,157), [Drawing.Color]::FromArgb(255,248,157,202))
    }
    [Drawing.Color[]]$palette = $common + $accentColors + @(
        [Drawing.Color]::FromArgb(255,91,57,40), [Drawing.Color]::FromArgb(255,151,101,70),
        [Drawing.Color]::FromArgb(255,213,162,116), [Drawing.Color]::FromArgb(255,255,220,174)
    )
    return $palette
}

function Render-G2dSprite([int]$sourceTopId, [Drawing.Color[]]$palette, [string]$outputPath) {
    $sourceRoot = Join-Path $GenericJobsRoot 'FFTIVC\data\enhanced\system\ffto\g2d'
    $top = [IO.File]::ReadAllBytes((Join-Path $sourceRoot "tex_$sourceTopId.bin"))
    $bottom = [IO.File]::ReadAllBytes((Join-Path $sourceRoot "tex_$($sourceTopId + 1).bin"))
    $image = [Drawing.Bitmap]::new(256, 488, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
        for ($y = 0; $y -lt 488; $y++) {
            $sheet = if ($y -lt 256) { $top } else { $bottom }
            $sheetY = if ($y -lt 256) { $y } else { $y - 256 }
            for ($x = 0; $x -lt 256; $x++) {
                # Enhanced G2D stores the PSP 4-bpp image doubled to 512x512.
                $packed = $sheet[(2 * $sheetY) * 256 + $x]
                $index = $packed -band 0x0F
                $image.SetPixel($x, $y, $palette[$index])
            }
        }
        $image.Save($outputPath, [Drawing.Imaging.ImageFormat]::Bmp)
    } finally { $image.Dispose() }
}

function New-IndexedG2dSprite([string]$templateBmp, [int]$sourceTopId, [Drawing.Color[]]$palette, [string]$outputPath) {
    # The enhanced G2D pages contain the actual Dark Knight animation frames.
    # Rebuild a 4-bpp PSP sheet from them so both the enhanced and fallback
    # renderer use the same character, rather than only recolouring a palette.
    $bytes = [IO.File]::ReadAllBytes($templateBmp)
    if ($bytes.Length -lt 1078 -or $bytes[0] -ne 0x42 -or $bytes[1] -ne 0x4D) {
        throw "Invalid indexed BMP template: $templateBmp"
    }
    $pixelOffset = [BitConverter]::ToInt32($bytes, 10)
    $width = [BitConverter]::ToInt32($bytes, 18)
    $height = [Math]::Abs([BitConverter]::ToInt32($bytes, 22))
    $bitsPerPixel = [BitConverter]::ToInt16($bytes, 28)
    if ($width -ne 256 -or $height -ne 488 -or $bitsPerPixel -ne 8) {
        throw "Expected an indexed 256x488 BMP template: $templateBmp"
    }
    $paletteOffset = 14 + [BitConverter]::ToInt32($bytes, 14)
    for ($i = 0; $i -lt 16; $i++) {
        $color = $palette[$i]
        $offset = $paletteOffset + $i * 4
        $bytes[$offset] = $color.B
        $bytes[$offset + 1] = $color.G
        $bytes[$offset + 2] = $color.R
        $bytes[$offset + 3] = 0
    }
    $sourceRoot = Join-Path $GenericJobsRoot 'FFTIVC\data\enhanced\system\ffto\g2d'
    $top = [IO.File]::ReadAllBytes((Join-Path $sourceRoot "tex_$sourceTopId.bin"))
    $bottom = [IO.File]::ReadAllBytes((Join-Path $sourceRoot "tex_$($sourceTopId + 1).bin"))
    $stride = (($width + 3) -band -4)
    $bottomUp = [BitConverter]::ToInt32($bytes, 22) -gt 0
    for ($y = 0; $y -lt $height; $y++) {
        $sheet = if ($y -lt 256) { $top } else { $bottom }
        $sheetY = if ($y -lt 256) { $y } else { $y - 256 }
        $bmpY = if ($bottomUp) { $height - 1 - $y } else { $y }
        for ($x = 0; $x -lt $width; $x++) {
            $bytes[$pixelOffset + $bmpY * $stride + $x] = $sheet[(2 * $sheetY) * 256 + $x] -band 0x0F
        }
    }
    [IO.File]::WriteAllBytes($outputPath, $bytes)
}

function Copy-Face([int]$sourceId, [int]$targetId) {
    $sourceTexture = Join-Path $GenericJobsRoot "FFTIVC\data\enhanced\ui\ffto\common\face\texture\wldface_${sourceId}_08_uitx.tex"
    $sourceParts = Join-Path $GenericJobsRoot "FFTIVC\data\enhanced\ui\ffto\common\face\textureparts\wldface_${sourceId}_08_uitx.utexpt"
    Copy-Item -LiteralPath $sourceTexture -Destination (Join-Path $faceTextureRoot "wldface_${targetId}_08_uitx.tex") -Force
    $bytes = [IO.File]::ReadAllBytes($sourceParts)
    $text = $partsEncoding.GetString($bytes).Replace("wldface_${sourceId}_08_uitx.tex", "wldface_${targetId}_08_uitx.tex")
    [IO.File]::WriteAllBytes((Join-Path $facePartsRoot "wldface_${targetId}_08_uitx.utexpt"), $partsEncoding.GetBytes($text))
}

function Copy-JobVisual([int]$targetId) {
    $sourceTextureRoot = Join-Path $GenericJobsRoot 'FFTIVC\data\enhanced\ui\ffto\icon\job_visual\texture'
    $sourcePartsRoot = Join-Path $GenericJobsRoot 'FFTIVC\data\enhanced\ui\ffto\icon\job_visual\textureparts'
    foreach ($gender in @('m', 'f')) {
        $sourceName = "jv_21_${gender}_uitx"
        $targetName = "jv_${targetId}_${gender}_uitx"
        Copy-Item -LiteralPath (Join-Path $sourceTextureRoot "$sourceName.tex") -Destination (Join-Path $jobVisualTextureRoot "$targetName.tex") -Force
        $bytes = [IO.File]::ReadAllBytes((Join-Path $sourcePartsRoot "$sourceName.utexpt"))
        $text = $partsEncoding.GetString($bytes).Replace("$sourceName.tex", "$targetName.tex")
        [IO.File]::WriteAllBytes((Join-Path $jobVisualPartsRoot "$targetName.utexpt"), $partsEncoding.GetBytes($text))
    }
}

function Build-Face([string]$bmpPath, [int]$targetId, [int]$partsTemplateId, [int]$portraitY = 456) {
    $source = [Drawing.Bitmap]::new($bmpPath)
    $indexed = Read-IndexedBmp $bmpPath $portraitY
    try {
        # Editor sheets store the 32x48 portrait rotated clockwise in a
        # 48x32 rectangle. Undo that rotation; never stretch it sideways.
        # The supplied utexpt describes a 520x388 atlas, NOT a 128x192 image.
        # Duplicate the static portrait into its base/eye/mouth tiles so all
        # native animation parts have valid coordinates and matching content.
        $face = [Drawing.Bitmap]::new(520, 388, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
        try {
            for ($y = 0; $y -lt 192; $y++) {
                for ($x = 0; $x -lt 128; $x++) {
                    # Read-IndexedBmp normalizes the portrait to the final rows;
                    # use palette 8 even when the BMP displays palette 0.
                    $index = $indexed.Indices[(456 + [int][Math]::Floor($x / 4)), (80 + 47 - [int][Math]::Floor($y / 4))] -band 15
                    $color = $indexed.Palette[128 + $index]
                    if ($color.R -eq 0 -and $color.G -eq 0 -and $color.B -eq 0) { $color = [Drawing.Color]::FromArgb(0,0,0,0) }
                    foreach ($tileY in @(1,195)) {
                        foreach ($tileX in @(1,131,261,391)) { $face.SetPixel($tileX + $x, $tileY + $y, $color) }
                    }
                }
            }
            $bmpOut = Join-Path $faceBuildRoot "wldface_${targetId}_08_uitx.bmp"
            $face.Save($bmpOut, [Drawing.Imaging.ImageFormat]::Bmp)
        } finally { $face.Dispose() }
    } finally { $source.Dispose() }

    & $FF16Tools img-conv -i $bmpOut | Out-Host
    $texOut = [IO.Path]::ChangeExtension($bmpOut, '.tex')
    Copy-Item -LiteralPath $texOut -Destination (Join-Path $faceTextureRoot "wldface_${targetId}_08_uitx.tex") -Force
    $template = Join-Path $GenericJobsRoot "FFTIVC\data\enhanced\ui\ffto\common\face\textureparts\wldface_${partsTemplateId}_08_uitx.utexpt"
    $bytes = [IO.File]::ReadAllBytes($template)
    $text = $partsEncoding.GetString($bytes).Replace("wldface_${partsTemplateId}_08_uitx.tex", "wldface_${targetId}_08_uitx.tex")
    [IO.File]::WriteAllBytes((Join-Path $facePartsRoot "wldface_${targetId}_08_uitx.utexpt"), $partsEncoding.GetBytes($text))
}

function Build-JobVisual([string]$bmpPath, [int]$targetId, [string]$gender) {
    $indexed = Read-IndexedBmp $bmpPath
    $source = [Drawing.Bitmap]::new(32, 40, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
    for ($y = 0; $y -lt 40; $y++) {
        for ($x = 0; $x -lt 32; $x++) {
            $index = $indexed.Indices[$y, $x] -band 15
            $color = if ($index -eq 0) { [Drawing.Color]::Transparent } else { $indexed.Palette[$index] }
            $source.SetPixel($x, $y, $color)
        }
    }
    try {
        $visual = [Drawing.Bitmap]::new(400, 652, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
        try {
            $graphics = [Drawing.Graphics]::FromImage($visual)
            try {
                $graphics.Clear([Drawing.Color]::Transparent)
                $graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
                $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::Half
                $graphics.DrawImage($source, [Drawing.Rectangle]::new(40,126,320,400), [Drawing.Rectangle]::new(0,0,32,40), [Drawing.GraphicsUnit]::Pixel)
            } finally { $graphics.Dispose() }
            $name = "jv_${targetId}_${gender}_uitx"
            $bmpOut = Join-Path $jobVisualBuildRoot "$name.bmp"
            $visual.Save($bmpOut, [Drawing.Imaging.ImageFormat]::Bmp)
            & $FF16Tools img-conv -i $bmpOut | Out-Host
            Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($bmpOut, '.tex')) -Destination (Join-Path $jobVisualTextureRoot "$name.tex") -Force
            $templateName = "jv_21_${gender}_uitx"
            $template = Join-Path $GenericJobsRoot "FFTIVC\data\enhanced\ui\ffto\icon\job_visual\textureparts\$templateName.utexpt"
            $bytes = [IO.File]::ReadAllBytes($template)
            $text = $partsEncoding.GetString($bytes).Replace("$templateName.tex", "$name.tex")
            [IO.File]::WriteAllBytes((Join-Path $jobVisualPartsRoot "$name.utexpt"), $partsEncoding.GetBytes($text))
        } finally { $visual.Dispose() }
    } finally { $source.Dispose() }
}

function Build-JobIcon([string]$imagePath, [int]$jobId, [Drawing.Rectangle]$crop, [string]$background) {
    $source = [Drawing.Bitmap]::new($imagePath)
    try {
        $icon = [Drawing.Bitmap]::new(60, 60, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
        try {
            $graphics = [Drawing.Graphics]::FromImage($icon)
            try {
                $graphics.Clear([Drawing.Color]::Transparent)
                $graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
                $destinationRect = if ($background -eq 'alpha') { [Drawing.Rectangle]::new(0,0,60,60) } else { [Drawing.Rectangle]::new(4,4,52,52) }
                $graphics.DrawImage($source, $destinationRect, $crop, [Drawing.GraphicsUnit]::Pixel)
            } finally { $graphics.Dispose() }

            # Remove the flat stock-image background while preserving the emblem.
            for ($y = 0; $y -lt $icon.Height; $y++) {
                for ($x = 0; $x -lt $icon.Width; $x++) {
                    $c = $icon.GetPixel($x, $y)
                    $transparent = if ($background -eq 'alpha') { $false } elseif ($background -eq 'light') {
                        ([Math]::Abs([int]$c.R - [int]$c.G) -lt 12 -and [Math]::Abs([int]$c.G - [int]$c.B) -lt 12 -and $c.R -gt 125)
                    } else {
                        ($c.R -lt 35 -and $c.G -lt 35 -and $c.B -lt 42)
                    }
                    if ($transparent) { $icon.SetPixel($x, $y, [Drawing.Color]::Transparent) }
                }
            }

            $name = "j_${jobId}_uitx"
            $bmpOut = Join-Path $jobVisualBuildRoot "$name.bmp"
            $icon.Save($bmpOut, [Drawing.Imaging.ImageFormat]::Bmp)
            & $FF16Tools img-conv -i $bmpOut | Out-Host
            Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($bmpOut, '.tex')) -Destination (Join-Path $jobIconTextureRoot "$name.tex") -Force

            $template = Join-Path $GenericJobsRoot 'FFTIVC\data\enhanced\ui\ffto\icon\job\textureparts\j_160_uitx.utexpt'
            $bytes = [IO.File]::ReadAllBytes($template)
            $text = $partsEncoding.GetString($bytes).Replace('j_160_uitx.tex', "$name.tex")
            [IO.File]::WriteAllBytes((Join-Path $jobIconPartsRoot "$name.utexpt"), $partsEncoding.GetBytes($text))
        } finally { $icon.Dispose() }
    } finally { $source.Dispose() }
}

function Build-Variant([string]$bmpPath, [int]$shapeId, [int]$faceTemplateId, [int]$visualId, [string]$gender) {
    Build-Body $bmpPath "rune_$gender"
    Build-Face $bmpPath $shapeId $faceTemplateId
    Build-JobVisual $bmpPath $visualId $gender
}

function Build-HolyVariant([string]$bmpPath, [int]$shapeId, [int]$faceTemplateId, [string]$gender, [int]$portraitY = 456) {
    Build-Body $bmpPath "holy_$gender" $portraitY
    Build-Face $bmpPath $shapeId $faceTemplateId $portraitY
    Build-JobVisual $bmpPath 22 $gender
}

function Build-Body([string]$bmpPath, [string]$name, [int]$portraitY = 456) {
    $sprite = Read-IndexedBmp $bmpPath $portraitY
    Write-G2dSheet $sprite 0 (Join-Path $visualResourceRoot "${name}_top.bin")
    Write-G2dSheet $sprite 256 (Join-Path $visualResourceRoot "${name}_bottom.bin")
    $sprOut = Join-Path $visualResourceRoot "$name.spr"
    if ($portraitY -eq 256) {
        & dotnet $spriteConverterDll $bmpPath $sprOut '--portrait-middle' | Out-Host
    } else {
        & dotnet $spriteConverterDll $bmpPath $sprOut | Out-Host
    }
    if ($LASTEXITCODE -ne 0) { throw "Full SPR conversion failed: $bmpPath" }
    Update-SprPalette $sprOut (Get-PaletteRange $sprite 0) (Get-PaletteRange $sprite 128)
    if (-not [string]::IsNullOrWhiteSpace($NativeSprRoot)) {
        # Repacking removes editor padding, not the original team/portrait
        # palettes. Preserve all sixteen native palette slots byte-for-byte.
        $native = [IO.File]::ReadAllBytes((Join-Path $NativeSprRoot "$name.spr"))
        if ($native.Length -lt 37376) { throw "Incomplete native SPR: $name" }
        $packed = [IO.File]::ReadAllBytes($sprOut)
        [Array]::Copy($native, 0, $packed, 0, 512)
        [IO.File]::WriteAllBytes($sprOut, $packed)
    }
    $length = (Get-Item -LiteralPath $sprOut).Length
    if ($length -gt 45056) { throw "SPR exceeds native staging buffer: $sprOut ($length bytes)" }
}

# Remove only the generated portraits for the previously colliding shapes.
foreach ($oldId in 163..166) {
    foreach ($oldPath in @(
        (Join-Path $faceTextureRoot "wldface_${oldId}_08_uitx.tex"),
        (Join-Path $facePartsRoot "wldface_${oldId}_08_uitx.utexpt")
    )) { if (Test-Path -LiteralPath $oldPath) { Remove-Item -LiteralPath $oldPath } }
}

Build-HolyVariant (Join-Path $HolySpriteRoot 'HolyKnight Male.BMP') 170 159 'm' $HolyMalePortraitY
Build-HolyVariant (Join-Path $HolySpriteRoot 'HolyKnight Female.bmp') 171 160 'f'
Build-Variant (Join-Path $RuneSpriteRoot 'Rune Knight Male.bmp') 172 161 23 'm'
Build-Variant (Join-Path $RuneSpriteRoot 'Rune Knight Female.bmp') 173 162 23 'f'

if (-not [string]::IsNullOrWhiteSpace($IconRoot)) {
    Build-JobIcon (Join-Path $IconRoot 'Holy Knight.png') 162 ([Drawing.Rectangle]::new(0,0,60,60)) 'alpha'
    Build-JobIcon (Join-Path $IconRoot 'Rune Knight.png') 163 ([Drawing.Rectangle]::new(0,0,60,60)) 'alpha'
} else {
    Build-JobIcon (Join-Path $HolySpriteRoot 'Icon Holy Knight.jfif') 162 ([Drawing.Rectangle]::new(72,24,244,220)) 'light'
    Build-JobIcon (Join-Path $RuneSpriteRoot 'icon Rune Knight.jfif') 163 ([Drawing.Rectangle]::new(18,18,244,244)) 'dark'
}

Write-Host 'GenericKnights sprite resources built.'
