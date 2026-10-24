Add-Type -AssemblyName System.Drawing
$root = (Get-Location).Path
$gis = Get-Content (Join-Path $root 'audit/batch2_krannert/krannert_gis_fid54_4326.json') -Raw | ConvertFrom-Json
$asset = Get-Content (Join-Path $root 'modular/manifest.json') -Raw | ConvertFrom-Json
$building = $asset.assets | Where-Object { $_.id -eq 'krannert_building' }
$originX = [double]$building.placement_origin_xy_m[0]
$originY = [double]$building.placement_origin_xy_m[1]
$bounds = Get-Content (Join-Path $root 'audit/batch2_krannert/structural_bounds_round3.json') -Raw | ConvertFrom-Json
$feature = $gis.features[0]
$cos = [Math]::Cos(40.4274 * [Math]::PI / 180.0)
$gisPts = [System.Collections.Generic.List[System.Drawing.PointF]]::new()
foreach ($pt in $feature.geometry.rings[0]) {
  $x = ([double]$pt[0] + 86.9137) * 111412.84 * $cos - $originX
  $y = ([double]$pt[1] - 40.4274) * 111040.0 - $originY
  $gisPts.Add([System.Drawing.PointF]::new([single]$x,[single]$y))
}
$wirePts = [System.Collections.Generic.List[System.Drawing.PointF]]::new()
foreach ($pt in $bounds.KRAN_Footprint_Reference_Wire.vertices_xy) {
  $wirePts.Add([System.Drawing.PointF]::new([single]([double]$pt[0]-$originX),[single]([double]$pt[1]-$originY)))
}
$wall = $bounds.KRAN_Exterior_Masonry_Walls.bounds
$wallMinX=[double]$wall[0][0]; $wallMaxX=[double]$wall[0][1]
$wallMinY=[double]$wall[1][0]; $wallMaxY=[double]$wall[1][1]
$bmp=[System.Drawing.Bitmap]::new(1500,1050)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(248,249,250))
$fontTitle=[System.Drawing.Font]::new('Segoe UI',24,[System.Drawing.FontStyle]::Bold)
$fontBody=[System.Drawing.Font]::new('Segoe UI',14,[System.Drawing.FontStyle]::Regular)
$fontSmall=[System.Drawing.Font]::new('Segoe UI',12,[System.Drawing.FontStyle]::Regular)
$ink=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(34,43,51))
$muted=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(72,84,96))
$g.DrawString('KRANNERT BUILDING — GIS / SOURCE FOOTPRINT OVERLAY', $fontTitle,$ink,45,24)
$g.DrawString('Feature 54 • source wire shown in building-local coordinates • north is up', $fontBody,$muted,48,69)
$plot=[System.Drawing.Rectangle]::new(100,120,1300,680)
$g.FillRectangle([System.Drawing.SolidBrush]::new([System.Drawing.Color]::White),$plot)
$scale=8.0; $cx=750.0; $cy=460.0
$mapPoint={ param($p) [System.Drawing.PointF]::new([single]($cx+$p.X*$scale),[single]($cy-$p.Y*$scale)) }
$gisScreen=[System.Drawing.PointF[]]::new($gisPts.Count)
for($i=0;$i -lt $gisPts.Count;$i++) { $gisScreen[$i]=&$mapPoint $gisPts[$i] }
$wireScreen=[System.Drawing.PointF[]]::new($wirePts.Count)
for($i=0;$i -lt $wirePts.Count;$i++) { $wireScreen[$i]=&$mapPoint $wirePts[$i] }
$fill=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(28,90,145,190))
$g.FillPolygon($fill,$gisScreen)
$gisPen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(35,115,176),4)
$gisPen.DashStyle=[System.Drawing.Drawing2D.DashStyle]::Dash
$g.DrawPolygon($gisPen,$gisScreen)
$wirePen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(192,54,89),2.5)
$g.DrawPolygon($wirePen,$wireScreen)
$wallRect=[System.Drawing.RectangleF]::new([single]($cx+$wallMinX*$scale),[single]($cy-$wallMaxY*$scale),[single](($wallMaxX-$wallMinX)*$scale),[single](($wallMaxY-$wallMinY)*$scale))
$wallPen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(220,137,44),3)
$wallPen.DashStyle=[System.Drawing.Drawing2D.DashStyle]::Dash
$g.DrawRectangle($wallPen,$wallRect.X,$wallRect.Y,$wallRect.Width,$wallRect.Height)
# North arrow and 10 m scale bar.
$g.DrawLine([System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(28,38,48),3),1320,225,1320,155)
$g.FillPolygon([System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(28,38,48)),[System.Drawing.PointF[]]@([System.Drawing.PointF]::new(1308,169),[System.Drawing.PointF]::new(1320,146),[System.Drawing.PointF]::new(1332,169)))
$g.DrawString('N',$fontBody,$ink,1310,124)
$scalePen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(28,38,48),5)
$g.DrawLine($scalePen,1250,748,1330,748)
$g.DrawLine($scalePen,1250,739,1250,757);$g.DrawLine($scalePen,1330,739,1330,757)
$g.DrawString('10 m',$fontSmall,$ink,1272,758)
# Legend.
$g.DrawLine($gisPen,140,835,195,835);$g.DrawString('Purdue GIS feature 54 (WGS84 → project local approximation)', $fontSmall,$ink,210,824)
$g.DrawLine($wirePen,140,865,195,865);$g.DrawString('Asset footprint wire (derived from this GIS feature; coincident by construction)', $fontSmall,$ink,210,854)
$g.DrawLine($wallPen,140,895,195,895);$g.DrawString('Masonry exterior AABB, for bounds screening only', $fontSmall,$ink,210,884)
$g.DrawString('Marker: (234.5345001, −412.7189941, 0), zero rotation, unit scale; coordinator read-only check matches manifest within 0.00002 m.', $fontSmall,$muted,48,928)
$g.DrawString('GIS and model footprint overlap is not independent as-built verification; wall AABB expands ~0.20 m beyond GIS bounds per side.', $fontSmall,$muted,48,952)
$g.DrawString('The source slab/paving pad is a flat rectangle; campus terrain, roads and exact paving extent remain master-context items.', $fontSmall,$muted,48,976)
$out=Join-Path $root 'audit/batch2_krannert/krannert_gis_footprint_overlay_r3.png'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose()
Write-Output $out
