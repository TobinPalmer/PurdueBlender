Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile((Resolve-Path 'audit\complete_knoy\ground_plan.png').Path)
$r=[System.Drawing.Rectangle]::new(380,130,390,220)
$c=$b.Clone($r,$b.PixelFormat)
$out=[System.Drawing.Bitmap]::new($c,1170,660)
$out.Save('audit\batch4_knoy\plan_diagonal_zoom.png',[System.Drawing.Imaging.ImageFormat]::Png)
$b.Dispose();$c.Dispose();$out.Dispose()
