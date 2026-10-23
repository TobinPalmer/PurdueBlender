Add-Type -AssemblyName System.Drawing
$basePath = Resolve-Path 'audit\complete_knoy\ground_plan.png'
$outPath = 'audit\batch4_knoy\footprint_registration_overlay.png'
$vertices = Get-Content 'audit\batch4_knoy\gis_vertices_local.json' -Raw | ConvertFrom-Json
$bmp = [System.Drawing.Bitmap]::FromFile($basePath.Path)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$pen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(220,0,110,210), 2.0)
$brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(245,255,255,255))
$font = [System.Drawing.Font]::new('Arial', 11, [System.Drawing.FontStyle]::Bold)
$pts = @()
foreach($v in $vertices){
  $x = ([double]$v[1]+46)/0.13 + 64
  $y = ([double]$v[0]+15)/0.126 + 100
  $pts += ,[System.Drawing.PointF]::new([single]$x,[single]$y)
}
$g.DrawPolygon($pen, [System.Drawing.PointF[]]$pts)
$anchors = @(@{id='A';i=26;x=60;y=97},@{id='B';i=25;x=64;y=353},@{id='C';i=14;x=776;y=261})
foreach($a in $anchors){
  $g.FillEllipse($brush,[single]($a.x-7),[single]($a.y-7),14,14)
  $g.DrawEllipse([System.Drawing.Pen]::new([System.Drawing.Color]::DarkOrange,2),[single]($a.x-7),[single]($a.y-7),14,14)
  $g.DrawString($a.id,$font,[System.Drawing.Brushes]::DarkOrange,[single]($a.x+8),[single]($a.y-12))
}
$g.Dispose();$bmp.Save($outPath,[System.Drawing.Imaging.ImageFormat]::Png);$bmp.Dispose()
