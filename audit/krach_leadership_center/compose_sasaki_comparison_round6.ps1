Add-Type -AssemblyName System.Drawing
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$referencePath = Join-Path $PSScriptRoot 'sasaki_krach_corner_view_reference.jpg'
$modelPath = Join-Path $PSScriptRoot 'source_preview.png'
$outputPath = Join-Path $PSScriptRoot 'sasaki_facade_comparison_round8.png'
$reference = [System.Drawing.Bitmap]::new($referencePath)
$model = [System.Drawing.Bitmap]::new($modelPath)
$canvas = [System.Drawing.Bitmap]::new(1800, 660)
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.Clear([System.Drawing.Color]::FromArgb(245, 245, 245))
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$font = [System.Drawing.Font]::new('Arial', 22, [System.Drawing.FontStyle]::Bold)
$brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(35, 35, 35))
$graphics.DrawString('Sasaki project photograph', $font, $brush, 24, 8)
$graphics.DrawString('Krach source model — matching oblique view', $font, $brush, 924, 8)
$graphics.DrawImage($reference, 20, 42, 880, 586)
$graphics.DrawImage($model, 920, 42, 860, 562)
$canvas.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$brush.Dispose(); $font.Dispose(); $graphics.Dispose()
$canvas.Dispose(); $model.Dispose(); $reference.Dispose()
Write-Output $outputPath
