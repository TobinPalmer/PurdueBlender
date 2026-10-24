Add-Type -AssemblyName System.Drawing
$root=(Get-Location).Path
$page=[System.Drawing.Bitmap]::new((Join-Path $root 'audit/batch2_krannert/aia65detail-32.png'))
$rect=[System.Drawing.Rectangle]::new(112,1120,1200,575)
$crop=$page.Clone($rect,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$out=Join-Path $root 'audit/batch2_krannert/krannert_architect_1965_photo_crop.png'
$crop.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose();$page.Dispose()
Write-Output $out
