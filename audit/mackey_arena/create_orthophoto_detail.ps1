Add-Type -AssemblyName System.Drawing
$src=[System.Drawing.Bitmap]::FromFile((Join-Path $PSScriptRoot 'orthophoto_registration_overlay.png'))
$rect=[System.Drawing.Rectangle]::new(610,235,260,285)
$crop=$src.Clone($rect,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$out=[System.Drawing.Bitmap]::new(780,855)
$g=[System.Drawing.Graphics]::FromImage($out);$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($crop,0,0,780,855);$g.Dispose()
$out.Save((Join-Path $PSScriptRoot 'north_sdac_registration_detail.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$out.Dispose();$crop.Dispose();$src.Dispose()
