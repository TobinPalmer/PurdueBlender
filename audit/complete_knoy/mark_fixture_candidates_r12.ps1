Add-Type -AssemblyName System.Drawing
$base=Split-Path $MyInvocation.MyCommand.Path
$src=(Resolve-Path (Join-Path $base 'knoy_typical_plan_crop.png')).Path
$meta=Get-Content (Join-Path $base 'typical_plan_fixture_candidates_r12.json') -Raw | ConvertFrom-Json
$img=[System.Drawing.Bitmap]::new($src);$g=[System.Drawing.Graphics]::FromImage($img)
$green=[System.Drawing.Color]::FromArgb(235,10,150,65);$blue=[System.Drawing.Color]::FromArgb(235,35,90,200)
foreach($f in $meta.candidates){$x=[float]$f.center_pixel[0];$y=[float]$f.center_pixel[1];$col=if($f.type -eq 'toilet'){$blue}else{$green};$pen=[System.Drawing.Pen]::new($col,1.4);$brush=[System.Drawing.SolidBrush]::new($col);$g.FillEllipse($brush,$x-3,$y-3,6,6);$pen.Dispose();$brush.Dispose()}
$font=[System.Drawing.Font]::new('Arial',8);$greenBrush=[System.Drawing.SolidBrush]::new($green);$blueBrush=[System.Drawing.SolidBrush]::new($blue)
$g.FillEllipse($greenBrush,14,14,8,8);$g.DrawString('interpreted basin symbol', $font,[System.Drawing.Brushes]::Black,27,11)
$g.FillEllipse($blueBrush,14,29,8,8);$g.DrawString('interpreted toilet symbol', $font,[System.Drawing.Brushes]::Black,27,26)
$out=Join-Path $base 'knoy_typical_plan_fixture_overlay_r12.png';$img.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$img.Dispose();$font.Dispose();$greenBrush.Dispose();$blueBrush.Dispose()
