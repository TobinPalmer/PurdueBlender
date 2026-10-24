Add-Type -AssemblyName System.Drawing
$root=(Get-Location).Path
$left=[System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/krannert_southeast_same_corner_r4.png'))
$right=[System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/krannert_southwest_same_corner_r4.png'))
$bmp=[System.Drawing.Bitmap]::new(2250,1220)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.Clear([System.Drawing.Color]::FromArgb(247,248,249))
$ink=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(31,40,49))
$muted=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(73,84,95))
$white=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
$title=[System.Drawing.Font]::new('Segoe UI',25,[System.Drawing.FontStyle]::Bold)
$label=[System.Drawing.Font]::new('Segoe UI',17,[System.Drawing.FontStyle]::Bold)
$body=[System.Drawing.Font]::new('Segoe UI',15,[System.Drawing.FontStyle]::Regular)
$g.DrawString('KRANNERT COURTYARD / RE-ENTRANT - TWO MODEL VIEWS',$title,$ink,38,24)
$a=[System.Drawing.Rectangle]::new(40,85,1060,700);$b=[System.Drawing.Rectangle]::new(1150,85,1060,700)
$g.FillRectangle($white,$a);$g.FillRectangle($white,$b)
$g.DrawImage($left,$a);$g.DrawImage($right,$b)
$g.DrawString('Temporary camera from southeast',$label,$ink,42,795)
$g.DrawString('Temporary camera from southwest',$label,$ink,1152,795)
$g.DrawString('The two angles show the modeled re-entrant/courtyard relationship from opposite oblique views. No available source in this round resolves whether its visible depth, openings and connecting surfaces match the as-built condition. The seam is preserved as uncertain; this is not an independent as-built check.',$body,$muted,[System.Drawing.RectangleF]::new(42,845,2150,125))
$g.DrawString('Renders use temporary cameras and a render-only ground plane after reopening krannert_building.blend. These objects are not saved into the source asset.',$body,$muted,[System.Drawing.RectangleF]::new(42,1000,2150,70))
$out=Join-Path $root 'audit/batch2_krannert/krannert_reentrant_two_views_r4.png'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$left.Dispose();$right.Dispose()
Write-Output $out
