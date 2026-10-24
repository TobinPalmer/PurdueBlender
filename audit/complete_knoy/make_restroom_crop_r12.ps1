Add-Type -AssemblyName System.Drawing
$base=Split-Path $MyInvocation.MyCommand.Path
$source=[System.Drawing.Bitmap]::new((Join-Path $base 'knoy_typical_plan_crop.png'))
$data=Get-Content (Join-Path $base 'typical_plan_fixture_candidates_r12.json') -Raw | ConvertFrom-Json
$rect=[System.Drawing.Rectangle]::new(90,735,82,160)
$scale=4;$margin=28
$out=[System.Drawing.Bitmap]::new(($rect.Width*$scale)+60,($rect.Height*$scale)+$margin)
$g=[System.Drawing.Graphics]::FromImage($out);$g.Clear([System.Drawing.Color]::White)
$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::Half
$dest=[System.Drawing.Rectangle]::new(0,0,$rect.Width*$scale,$rect.Height*$scale)
$g.DrawImage($source,$dest,$rect,[System.Drawing.GraphicsUnit]::Pixel)
$green=[System.Drawing.Color]::FromArgb(235,10,150,65);$blue=[System.Drawing.Color]::FromArgb(235,35,90,200)
$gb=[System.Drawing.SolidBrush]::new($green);$bb=[System.Drawing.SolidBrush]::new($blue)
foreach($f in $data.candidates){$x=([float]$f.center_pixel[0]-$rect.X)*$scale;$y=([float]$f.center_pixel[1]-$rect.Y)*$scale;$brush=if($f.type -eq 'toilet'){$bb}else{$gb};$g.FillEllipse($brush,$x-4,$y-4,8,8)}
$font=[System.Drawing.Font]::new('Arial',8);$g.FillEllipse($gb,8,($rect.Height*$scale)+8,8,8);$g.DrawString('basin symbol interpretation',$font,[System.Drawing.Brushes]::Black,21,($rect.Height*$scale)+5)
$g.FillEllipse($bb,190,($rect.Height*$scale)+8,8,8);$g.DrawString('toilet symbol interpretation',$font,[System.Drawing.Brushes]::Black,203,($rect.Height*$scale)+5)
$out.Save((Join-Path $base 'knoy_typical_plan_restroom_detail_r12.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$out.Dispose();$source.Dispose();$gb.Dispose();$bb.Dispose();$font.Dispose()
