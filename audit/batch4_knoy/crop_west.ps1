Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile((Resolve-Path 'audit\complete_knoy\ground_plan.png').Path)
$r=[System.Drawing.Rectangle]::new(48,90,140,260)
$c=$b.Clone($r,$b.PixelFormat)
$out=[System.Drawing.Bitmap]::new($c,700,1300)
$out.Save('audit\batch4_knoy\plan_west_core_zoom.png',[System.Drawing.Imaging.ImageFormat]::Png)
$b.Dispose();$c.Dispose();$out.Dispose()
