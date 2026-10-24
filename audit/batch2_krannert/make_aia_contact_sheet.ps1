Add-Type -AssemblyName System.Drawing
$folder=Join-Path (Get-Location).Path 'audit/batch2_krannert'
$files=Get-ChildItem (Join-Path $folder 'aia65page-*.jpg') | Sort-Object Name
$cellW=140;$cellH=180;$cols=8;$rows=[math]::Ceiling($files.Count/$cols)
$bmp=[System.Drawing.Bitmap]::new($cellW*$cols,$cellH*$rows)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::White)
$font=[System.Drawing.Font]::new('Arial',10)
for($i=0;$i -lt $files.Count;$i++) {
  $im=[System.Drawing.Image]::FromFile($files[$i].FullName)
  $x=($i%$cols)*$cellW+5;$y=[math]::Floor($i/$cols)*$cellH+18
  $g.DrawString([string]($i+1),$font,[System.Drawing.Brushes]::Black,$x,$y-16)
  $g.DrawImage($im,$x,$y,130,155)
  $im.Dispose()
}
$out=Join-Path $folder 'indiana_architect_1965_contact.jpg'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Jpeg)
$g.Dispose();$bmp.Dispose()
Write-Output $out
