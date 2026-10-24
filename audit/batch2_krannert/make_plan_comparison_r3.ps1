Add-Type -AssemblyName System.Drawing
$root = (Get-Location).Path
$src = [System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/krannert_mel_2f_plan_source-1.png'))
$mdl = [System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/parrish_plan_r2.png'))
$bmp = [System.Drawing.Bitmap]::new(2200, 1370)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.Clear([System.Drawing.Color]::FromArgb(246,247,248))
$ink = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(30,38,46))
$muted = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(70,80,90))
$white = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
$fontTitle = [System.Drawing.Font]::new('Segoe UI', 26, [System.Drawing.FontStyle]::Bold)
$fontLabel = [System.Drawing.Font]::new('Segoe UI', 18, [System.Drawing.FontStyle]::Bold)
$fontText = [System.Drawing.Font]::new('Segoe UI', 14, [System.Drawing.FontStyle]::Regular)
$fontSmall = [System.Drawing.Font]::new('Segoe UI', 11, [System.Drawing.FontStyle]::Regular)
$g.DrawString('KRANNERT 2F: SOURCE PLAN + MODEL COMPARISON', $fontTitle, $ink, 40, 22)
$g.DrawString('Purdue / McGee Design House • 2010 “2nd Floor Furniture Plan”', $fontLabel, $muted, 45, 75)
$g.DrawString('Current saved source • Parrish Library interior render, round 2', $fontLabel, $muted, 1130, 75)
$srcRect = [System.Drawing.Rectangle]::new(40,115,1040,675)
$mdlRect = [System.Drawing.Rectangle]::new(1130,145,1020,650)
$g.FillRectangle($white, $srcRect); $g.FillRectangle($white, $mdlRect)
$g.DrawImage($src, $srcRect)
$g.DrawImage($mdl, $mdlRect)
$g.DrawString('Plan source URL: https://lib.purdue.edu/wp-content/uploads/2024/04/schematic.pdf', $fontText, $ink, 45, 815)
$g.DrawString('Source sheet says “not to scale.” It is an older furniture plan, not an as-built survey or a dimensional registration.', $fontText, $ink, 45, 845)
$g.DrawString('The current model uses estimated room/furniture XY; the 2026 Parrish refresh was documented as work in progress.', $fontText, $ink, 45, 875)
$g.DrawString('Side-by-side evidence only: no overlay, coordinate tie, meter scale, or current-installation claim is made.', $fontText, $ink, 45, 905)
$g.DrawString('Purdue Libraries PDF, retrieved 2026-10-24; page 1 of 2.', $fontSmall, $muted, 45, 960)
$out = Join-Path $root 'audit/batch2_krannert/parrish_plan_source_comparison_r3.png'
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose(); $src.Dispose(); $mdl.Dispose()
Write-Output $out
