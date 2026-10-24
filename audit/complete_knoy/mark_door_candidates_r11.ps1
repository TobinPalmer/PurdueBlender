Add-Type -AssemblyName System.Drawing
$base=Split-Path $MyInvocation.MyCommand.Path
$meta=Get-Content (Join-Path $base 'typical_plan_door_candidates_r11.json') -Raw | ConvertFrom-Json
$src=(Resolve-Path (Join-Path $base 'knoy_typical_plan_crop.png')).Path
$img=[System.Drawing.Bitmap]::new($src);$g=[System.Drawing.Graphics]::FromImage($img)
$pen=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(230,20,135,65),2)
$font=[System.Drawing.Font]::new('Arial',10);$brush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(245,20,105,55))
foreach($d in $meta.candidate_doors){$x=[float]$d.source_pixel_center[0];$y=[float]$d.source_pixel_center[1];$g.DrawEllipse($pen,$x-6,$y-6,12,12);$g.DrawString($d.id.ToString(),$font,$brush,$x+7,$y-8)}
$out=Join-Path $base 'knoy_typical_plan_doors_source_overlay_r11.png';$img.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$img.Dispose();$pen.Dispose();$font.Dispose();$brush.Dispose()
