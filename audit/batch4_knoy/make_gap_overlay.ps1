Add-Type -AssemblyName System.Drawing
$bmp=[System.Drawing.Bitmap]::FromFile((Resolve-Path 'audit\complete_knoy\ground_plan.png').Path)
$g=[System.Drawing.Graphics]::FromImage($bmp);$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$segments=@(
  @(@(100,158),@(100,298)),@(@(118,143),@(485,143)),@(@(118,321),@(228,321)),@(@(246,294),@(302,294)),@(@(320,278),@(373,225)),@(@(406,230),@(505,327)),@(@(524,313),@(627,211)),@(@(645,228),@(708,290)),@(@(143,165),@(143,290)),@(@(203,165),@(203,290)),@(@(294,165),@(294,211)),@(@(203,225),@(283,225)),@(@(203,260),@(283,260)),@(@(225,246),@(225,282)),@(@(341,165),@(341,210)),@(@(378,165),@(378,208)),@(@(414,165),@(414,180)),@(@(420,243),@(503,326)),@(@(443,221),@(526,304)),@(@(468,198),@(552,281)),@(@(491,175),@(575,258)),@(@(518,152),@(600,235)),@(@(438,262),@(539,161)),@(@(460,285),@(560,185)),@(@(483,309),@(584,208)),@(@(547,285),@(624,208)),@(@(571,308),@(647,231))
)
foreach($i in 8..26){
  $a=$segments[$i][0];$z=$segments[$i][1];$dx=$z[0]-$a[0];$dy=$z[1]-$a[1];$len=[Math]::Sqrt($dx*$dx+$dy*$dy)
  if($len -le 17){continue}
  $x=($a[0]+$z[0])/2;$y=($a[1]+$z[1])/2
  $g.FillEllipse([System.Drawing.Brushes]::Yellow,[single]($x-5),[single]($y-5),10,10)
  $g.DrawEllipse([System.Drawing.Pen]::new([System.Drawing.Color]::Black,1),[single]($x-5),[single]($y-5),10,10)
  $g.DrawString([string]$i,[System.Drawing.Font]::new('Arial',8,[System.Drawing.FontStyle]::Bold),[System.Drawing.Brushes]::Black,[single]($x+4),[single]($y+4))
}
$g.Dispose();$bmp.Save('audit\batch4_knoy\current_gap_overlay.png',[System.Drawing.Imaging.ImageFormat]::Png);$bmp.Dispose()
