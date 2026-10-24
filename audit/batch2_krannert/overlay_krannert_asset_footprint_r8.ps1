Add-Type -AssemblyName System.Drawing
$root=(Get-Location).Path
$src=Join-Path $root 'audit/batch2_krannert/indiana_ortho_krannert_2023_crop.jpg'
$gis=Get-Content (Join-Path $root 'audit/batch2_krannert/krannert_gis_fid54_4326.json') -Raw | ConvertFrom-Json
$asset=Get-Content (Join-Path $root 'audit/batch2_krannert/asset_footprint_round8.json') -Raw | ConvertFrom-Json
$base=[System.Drawing.Image]::FromFile($src);$W=$base.Width;$H=$base.Height
$bmp=[System.Drawing.Bitmap]::new($W,($H+210));$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias;$g.Clear([System.Drawing.Color]::White);$g.DrawImage($base,0,80,$W,$H)
$header=[System.Drawing.Font]::new('Segoe UI',24,[System.Drawing.FontStyle]::Bold);$body=[System.Drawing.Font]::new('Segoe UI',15,[System.Drawing.FontStyle]::Regular);$small=[System.Drawing.Font]::new('Segoe UI',12,[System.Drawing.FontStyle]::Regular)
$ink=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(20,32,42));$muted=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(56,68,78))
$g.DrawString('KRANNERT — SAVED-ASSET / ORTHOPHOTO FOOTPRINT CHECK',$header,$ink,25,15)
$g.DrawString('Purdue GIS FID 54 ring and roof-deck perimeter extracted from the reopened source blend; north is up',$body,$muted,28,50)
$minLon=-86.9128;$maxLon=-86.9092;$minLat=40.4227875;$maxLat=40.4248125
function To-Point($coords) { $pts=[System.Drawing.PointF[]]::new($coords.Count);for($i=0;$i -lt $coords.Count;$i++){ $lon=[double]$coords[$i][0];$lat=[double]$coords[$i][1];$x=($lon-$minLon)/($maxLon-$minLon)*$W;$y=80+($maxLat-$lat)/($maxLat-$minLat)*$H;$pts[$i]=[System.Drawing.PointF]::new([single]$x,[single]$y)};return ,$pts }
$gisPts=To-Point $gis.features[0].geometry.rings[0]
$assetPts=To-Point $asset.wgs84_ring_from_project_approximation
$blue=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(245,32,71,205),5)
$orange=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(245,255,142,0),2);$orange.DashStyle=[System.Drawing.Drawing2D.DashStyle]::Dash
$g.DrawPolygon($blue,$gisPts);$g.DrawPolygon($orange,$assetPts)
$g.FillRectangle([System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(245,32,71,205)),28,995,48,5);$g.DrawString('Purdue GIS ring FID 54',$body,$ink,88,982)
$g.FillRectangle([System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(245,255,142,0)),28,1023,48,5);$g.DrawString('Saved roof-deck perimeter (Blender 5.2.3)', $body,$ink,88,1010)
$g.DrawString('The saved roof-deck ring is derived from FID 54; near-exact overlap checks asset transform/conversion, not independent as-built fit.',$small,$muted,28,1050)
$g.DrawString('Orthophoto: Indiana GIO 2023 spring cycle, nominal 6-in cells, CC0. No translation, rotation or scale was fitted to the image.',$small,$muted,28,1075)
$out=Join-Path $root 'audit/batch2_krannert/krannert_asset_footprint_ortho_overlay_r8.png';$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$base.Dispose();Write-Output $out
