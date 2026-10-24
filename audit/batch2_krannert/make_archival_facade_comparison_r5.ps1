Add-Type -AssemblyName System.Drawing
$root=(Get-Location).Path
$src=[System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/krannert_architect_1965_photo_crop.png'))
$mdl=[System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/krannert_south_front_r4.png'))
$bmp=[System.Drawing.Bitmap]::new(2250,1450)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.Clear([System.Drawing.Color]::FromArgb(247,248,249))
$ink=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(31,40,49))
$muted=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(73,84,95))
$white=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
$title=[System.Drawing.Font]::new('Segoe UI',25,[System.Drawing.FontStyle]::Bold)
$label=[System.Drawing.Font]::new('Segoe UI',17,[System.Drawing.FontStyle]::Bold)
$body=[System.Drawing.Font]::new('Segoe UI',14,[System.Drawing.FontStyle]::Regular)
$small=[System.Drawing.Font]::new('Segoe UI',10,[System.Drawing.FontStyle]::Regular)
$g.DrawString('KRANNERT FACADE - 1965 ARCHIVAL PHOTO / MODEL COMPARISON',$title,$ink,38,25)
$p1=[System.Drawing.Rectangle]::new(40,90,1060,700);$p2=[System.Drawing.Rectangle]::new(1150,90,1060,700)
$g.FillRectangle($white,$p1);$g.FillRectangle($white,$p2)
$g.DrawImage($src,$p1);$g.DrawImage($mdl,$p2)
$g.DrawString('Indiana Architect, October 1965, p. 32',$label,$ink,43,810)
$g.DrawString('Reopened source model - south/front view, R4',$label,$ink,1153,810)
$g.DrawString('Contemporary architectural-journal photo labels the Krannert Building as selected for exhibition. It documents the original facade appearance: repeated narrow vertical glazing in broad light piers, a dark/recessed ground level, flat roof edge, and low site reflecting pool. The photo is historical and perspective-distorted.',$body,$muted,[System.Drawing.RectangleF]::new(42,858,1030,140))
$g.DrawString('The source shows the modeled facade rhythm and massing qualitatively, but window cadence, surface dimensions, camera projection and current condition are not registered or measured. Model ground context is not the historical reflecting pool.',$body,$muted,[System.Drawing.RectangleF]::new(1152,858,1030,140))
$g.DrawString('Caption on page 32 credits Walter Scholer & Associates as architect and K. H. Kettlehut as general contractor. This image supports original visible design only; it does not validate current roof/equipment, heights, hidden/courtyard faces, GIS fit, or exact material/color.',$body,$ink,[System.Drawing.RectangleF]::new(42,1030,2160,95))
$g.DrawString('Source PDF: https://usmodernist.org/AIAIN/AIAIN-1965-10.pdf | Indiana Architect, October 1965, p. 32; locally retained as indiana_architect_1965_10.pdf with page crop krannert_architect_1965_photo_crop.png. Model render: krannert_south_front_r4.png.',$small,$muted,[System.Drawing.RectangleF]::new(42,1150,2160,55))
$out=Join-Path $root 'audit/batch2_krannert/krannert_archival_facade_comparison_r5.png'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$src.Dispose();$mdl.Dispose()
Write-Output $out
