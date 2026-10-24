Add-Type -AssemblyName System.Drawing
$base=Split-Path $MyInvocation.MyCommand.Path
$photo=[System.Drawing.Bitmap]::new((Join-Path $base 'ref_purdue_profile_knoy_facade_r8.jpg'))
$model=[System.Drawing.Bitmap]::new((Join-Path $base 'knoy_entrance_detail_material_r13.png'))
$W=2500;$H=890;$header=58;$label=48;$footer=104;$gap=35;$pad=24
$panelW=[int](($W-2*$pad-$gap)/2);$panelH=$H-$header-$label-$footer-2*$pad
$canvas=[System.Drawing.Bitmap]::new($W,$H);$g=[System.Drawing.Graphics]::FromImage($canvas)
$g.Clear([System.Drawing.Color]::FromArgb(246,247,248));$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$titleFont=[System.Drawing.Font]::new('Arial',22,[System.Drawing.FontStyle]::Bold)
$labelFont=[System.Drawing.Font]::new('Arial',15,[System.Drawing.FontStyle]::Bold)
$noteFont=[System.Drawing.Font]::new('Arial',12)
$g.DrawString('KNOY HALL — ENTRANCE VISUAL EVIDENCE', $titleFont,[System.Drawing.Brushes]::Black,$pad,10)
$rects=@([System.Drawing.Rectangle]::new($pad,$header,$panelW,$panelH),[System.Drawing.Rectangle]::new(($pad+$panelW+$gap),$header,$panelW,$panelH))
$images=@($photo,$model)
for($i=0;$i -lt 2;$i++){
 $r=$rects[$i];$g.FillRectangle([System.Drawing.Brushes]::White,$r)
 $im=$images[$i];$scale=[Math]::Min($r.Width/$im.Width,$r.Height/$im.Height);$dw=[int]($im.Width*$scale);$dh=[int]($im.Height*$scale);$dx=$r.X+[int](($r.Width-$dw)/2);$dy=$r.Y+[int](($r.Height-$dh)/2)
 $g.DrawImage($im,$dx,$dy,$dw,$dh)
}
$g.DrawString('Purdue-hosted photo (undated, uncalibrated perspective)',$labelFont,[System.Drawing.Brushes]::Black,$pad,($header+$panelH+8))
$g.DrawString('Saved model with procedural brick/glazing (schematic)',$labelFont,[System.Drawing.Brushes]::Black,($pad+$panelW+$gap),($header+$panelH+8))
$note='Qualitative visual comparison only: red/brown brick sign wall, entrance lettering, pale horizontal trim and dark glazing are visible. Camera, dimensions, material specification and full facade rhythm are not calibrated by this single photo.'
$g.DrawString($note,$noteFont,[System.Drawing.Brushes]::Black,[System.Drawing.RectangleF]::new($pad,($H-$footer+10),($W-2*$pad),($footer-12)))
$canvas.Save((Join-Path $base 'knoy_entrance_photo_model_comparison_r13.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$photo.Dispose();$model.Dispose();$canvas.Dispose();$g.Dispose();$titleFont.Dispose();$labelFont.Dispose();$noteFont.Dispose()
