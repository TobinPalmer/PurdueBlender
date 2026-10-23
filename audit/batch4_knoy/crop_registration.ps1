Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile((Resolve-Path 'audit\batch4_knoy\footprint_registration_overlay.png').Path)
$r=[System.Drawing.Rectangle]::new(40,25,360,140)
$c=$b.Clone($r,$b.PixelFormat)
$out=[System.Drawing.Bitmap]::new($c,1080,420)
$out.Save('audit\batch4_knoy\registration_nw_zoom.png',[System.Drawing.Imaging.ImageFormat]::Png)
$b.Dispose();$c.Dispose();$out.Dispose()
