Add-Type -AssemblyName System.Drawing
$img=[System.Drawing.Bitmap]::FromFile((Join-Path $PSScriptRoot 'indiana_orthophoto_2023.jpg'))
$g=[System.Drawing.Graphics]::FromImage($img)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$j=Get-Content (Join-Path $PSScriptRoot 'ortho_overlay_vectors.json') -Raw | ConvertFrom-Json
$xmin=-9675753.0;$xmax=-9675103.0;$ymin=4928874.778571429;$ymax=4929431.921428571
function Pt($p) {
  $ax=-209.59000396728516;$ay=671.8374938964844
  $cx=[double]$p[0]+$ax;$cy=[double]$p[1]+$ay
  $lon=$cx/(111412.84*[Math]::Cos(40.4274*[Math]::PI/180.0))-86.9137
  $lat=$cy/111040.0+40.4274
  $mx=6378137.0*$lon*[Math]::PI/180.0
  $my=6378137.0*[Math]::Log([Math]::Tan([Math]::PI/4.0+$lat*[Math]::PI/360.0))
  return [System.Drawing.PointF]::new([single](($mx-$xmin)/($xmax-$xmin)*$img.Width),[single](($ymax-$my)/($ymax-$ymin)*$img.Height))
}
function DrawPoly($points,$color,$width) {
  $arr=[System.Collections.Generic.List[System.Drawing.PointF]]::new()
  foreach($p in $points){$arr.Add((Pt $p))}
  $pen=[System.Drawing.Pen]::new($color,$width);$g.DrawPolygon($pen,$arr.ToArray());$pen.Dispose()
}
DrawPoly $j.full_ring_local ([System.Drawing.Color]::FromArgb(230,255,45,35)) 2
DrawPoly $j.north_lobe_local ([System.Drawing.Color]::FromArgb(255,255,220,0)) 4
DrawPoly $j.east_single_story_trace ([System.Drawing.Color]::Lime) 4
DrawPoly $j.west_single_story_trace ([System.Drawing.Color]::Magenta) 4
$circle=[System.Collections.Generic.List[System.Drawing.PointF]]::new()
for($i=0;$i -lt 96;$i++){ $a=2.0*[Math]::PI*$i/96.0; $xy=[double[]]@([double]([Math]::Cos($a)*48.225),[double]([Math]::Sin($a)*48.225-14.1375)); $circle.Add((Pt $xy)) }
$pen=[System.Drawing.Pen]::new([System.Drawing.Color]::Cyan,3);$g.DrawPolygon($pen,$circle.ToArray());$pen.Dispose()
$font=[System.Drawing.Font]::new('Arial',18,[System.Drawing.FontStyle]::Bold)
$brush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::Yellow)
$g.DrawString('Red: composite GIS | Yellow: SDAC roof seam | Lime/Magenta: low-roof photo traces | Cyan: arena shell',$font,$brush,18,18)
# North arrow and a map-space scale bar; the image is north-up in EPSG:3857.
$pen=[System.Drawing.Pen]::new([System.Drawing.Color]::White,5);$pen.StartCap='Round';$pen.EndCap='ArrowAnchor';$g.DrawLine($pen,1360,95,1360,43);$pen.Dispose()
$small=[System.Drawing.Font]::new('Arial',18,[System.Drawing.FontStyle]::Bold)
$scalePx=[single](50.0/($xmax-$xmin)*$img.Width);$sx=[single]($img.Width-160);$sy=[single]($img.Height-35)
$bg=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(170,0,0,0));$g.FillRectangle($bg,$sx-10,$sy-48,155,60);$bg.Dispose()
$sp=[System.Drawing.Pen]::new([System.Drawing.Color]::White,7);$g.DrawLine($sp,$sx,$sy,$sx+$scalePx,$sy);$sp.Dispose()
$g.DrawString('50 m',$small,[System.Drawing.Brushes]::White,$sx,$sy-42);$small.Dispose()
$g.Dispose();$img.Save((Join-Path $PSScriptRoot 'orthophoto_registration_overlay.png'),[System.Drawing.Imaging.ImageFormat]::Png);$img.Dispose()

