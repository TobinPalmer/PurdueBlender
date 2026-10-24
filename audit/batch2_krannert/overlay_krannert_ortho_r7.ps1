Add-Type -AssemblyName System.Drawing
$root = (Get-Location).Path
$src = Join-Path $root 'audit/batch2_krannert/indiana_ortho_krannert_2023_crop.jpg'
$gis = Get-Content (Join-Path $root 'audit/batch2_krannert/krannert_gis_fid54_4326.json') -Raw | ConvertFrom-Json
$base = [System.Drawing.Image]::FromFile($src)
$W=$base.Width; $H=$base.Height
$bmp=[System.Drawing.Bitmap]::new($W,($H+190))
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::White)
$g.DrawImage($base,0,80,$W,$H)
$header=[System.Drawing.Font]::new('Segoe UI',24,[System.Drawing.FontStyle]::Bold)
$body=[System.Drawing.Font]::new('Segoe UI',15,[System.Drawing.FontStyle]::Regular)
$small=[System.Drawing.Font]::new('Segoe UI',12,[System.Drawing.FontStyle]::Regular)
$ink=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(20,32,42))
$muted=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(56,68,78))
$g.DrawString('KRANNERT — INDEPENDENT ORTHOPHOTO FOOTPRINT CHECK', $header,$ink,25,15)
$g.DrawString('Purdue GIS BuildingShapesZip4 FID 54 outline over Indiana 2023 aerial; north is up', $body,$muted,28,50)
# The downloaded crop extent, same WGS84 bbox used for the ImageServer export.
$minLon=-86.9128; $maxLon=-86.9092; $minLat=40.4227875; $maxLat=40.4248125
$ring=$gis.features[0].geometry.rings[0]
$pts=[System.Drawing.PointF[]]::new($ring.Count)
foreach($i in 0..($ring.Count-1)) {
  $lon=[double]$ring[$i][0]; $lat=[double]$ring[$i][1]
  $x=($lon-$minLon)/($maxLon-$minLon)*$W
  $y=80+($maxLat-$lat)/($maxLat-$minLat)*$H
  $pts[$i]=[System.Drawing.PointF]::new([single]$x,[single]$y)
}
$pen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(245,32,71,205),4)
$g.DrawPolygon($pen,$pts)
# Add a modest legend and source limits in the footer.
$g.FillRectangle([System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(245,32,71,205)),28,988,55,5)
$g.DrawString('GIS polygon FID 54', $body,$ink,95,976)
$g.DrawString('The GIS outline and model footprint wire share the same source geometry; this aerial is an independent visual cross-check, not a surveyed-shell measurement.', $small,$muted,28,1002)
$g.DrawString('Indiana GIO 2023 orthophoto: nominal 6-inch cells, CC0. GIS ring plotted directly in returned WGS84 extent; no image fit.', $small,$muted,28,1027)
$out=Join-Path $root 'audit/batch2_krannert/krannert_2023_orthophoto_footprint_overlay_r7.png'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$base.Dispose()
Write-Output $out



