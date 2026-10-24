Add-Type -AssemblyName System.Drawing
$root=(Get-Location).Path
$imCurrent=[System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/krannert_current_exterior_purdue.jpg'))
$imModel=[System.Drawing.Image]::FromFile((Join-Path $root 'audit/batch2_krannert/krannert_southwest_same_corner_r4.png'))
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
$g.DrawString('KRANNERT EXTERIOR - QUALITATIVE CORNER COMPARISON / ROUND 4',$title,$ink,38,25)
$p1=[System.Drawing.Rectangle]::new(40,90,1060,700)
$p2=[System.Drawing.Rectangle]::new(1150,90,1060,700)
$g.FillRectangle($white,$p1);$g.FillRectangle($white,$p2)
$g.DrawImage($imCurrent,$p1);$g.DrawImage($imModel,$p2)
$g.DrawString('Official Purdue event photo - date not provided',$label,$ink,43,810)
$g.DrawString('Model: reopened source, southwest corner view - R4',$label,$ink,1153,810)
$g.DrawString('Visible cues include warm light stone, narrow dark vertical glazing, a darker ground-level band and a projecting entry. This image is not a measured elevation.',$body,$muted,[System.Drawing.RectangleF]::new(42,858,1030,130))
$g.DrawString('This model view is framed to show the broad facade and return. The repeating openings, camera projection and corner registration are not calibrated to the photograph.',$body,$muted,[System.Drawing.RectangleF]::new(1152,858,1030,130))
$g.DrawString('Visual comparison only; not a photogrammetric match, survey, or verification of hidden elevations. No roof, footprint, floor-height, window-opening, canopy, or courtyard-seam geometry changed in R4. The courtyard/re-entrant seam remains unresolved.',$body,$ink,[System.Drawing.RectangleF]::new(42,1010,2160,90))
$g.DrawString('Photo source: https://events.purdue.edu/krannert_building | local image krannert_current_exterior_purdue.jpg | capture date unknown. Model: krannert_southwest_same_corner_r4.png, rendered from a temporary camera after reopening.',$small,$muted,[System.Drawing.RectangleF]::new(42,1120,2160,45))
$g.DrawString('R4 material scope: qualitative warm stone, charcoal glazing, and red-brown ground band only. Non-directional masonry variation is not a claim about brick coursing or precise dimensions.',$small,$muted,[System.Drawing.RectangleF]::new(42,1170,2160,45))
$out=Join-Path $root 'audit/batch2_krannert/krannert_exterior_source_comparison_r4.png'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$imCurrent.Dispose();$imModel.Dispose()
Write-Output $out
