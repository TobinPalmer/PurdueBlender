Add-Type -AssemblyName System.Drawing
$b=[System.Drawing.Bitmap]::FromFile((Resolve-Path 'audit\complete_knoy\ground_plan.png').Path)
$g=[System.Drawing.Graphics]::FromImage($b)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$segments=@(
  @(@(100,158),@(100,298)),@(@(118,143),@(485,143)),@(@(118,321),@(228,321)),@(@(246,294),@(302,294)),@(@(320,278),@(373,225)),@(@(406,230),@(505,327)),@(@(524,313),@(627,211)),@(@(645,228),@(708,290)),@(@(143,165),@(143,290)),@(@(203,165),@(203,290)),@(@(294,165),@(294,211)),@(@(203,225),@(283,225)),@(@(203,260),@(283,260)),@(@(225,246),@(225,282)),@(@(341,165),@(341,210)),@(@(378,165),@(378,208)),@(@(414,165),@(414,180)),@(@(420,243),@(503,326)),@(@(443,221),@(526,304)),@(@(468,198),@(552,281)),@(@(491,175),@(575,258)),@(@(518,152),@(600,235)),@(@(438,262),@(539,161)),@(@(460,285),@(560,185)),@(@(483,309),@(584,208)),@(@(547,285),@(624,208)),@(@(571,308),@(647,231))
)
for($i=0;$i -lt $segments.Count;$i++){
  $a=$segments[$i][0];$z=$segments[$i][1]
  $p1=[System.Drawing.PointF]::new([single]$a[0],[single]$a[1]);$p2=[System.Drawing.PointF]::new([single]$z[0],[single]$z[1])
  $color=[System.Drawing.Color]::FromArgb(220,180,30,110)
  $pen=[System.Drawing.Pen]::new($color,2)
  if($i -ge 8){
    $dx=$z[1]-$a[1];$dy=$z[0]-$a[0];$len=[Math]::Sqrt($dx*$dx+$dy*$dy)
    if($len -gt 17){
      $t0=([Math]::Max(0,($len-8.1)/2)/$len);$t1=1-$t0
      $pA=[System.Drawing.PointF]::new([single]($a[0]+$dx*0),[single]($a[1]+$dy*0))
      $pB=[System.Drawing.PointF]::new([single]($a[0]+$dx*$t0),[single]($a[1]+$dy*$t0))
      $pC=[System.Drawing.PointF]::new([single]($a[0]+$dx*$t1),[single]($a[1]+$dy*$t1))
      $pD=[System.Drawing.PointF]::new([single]$z[0],[single]$z[1])
      $g.DrawLine($pen,$pA,$pB);$g.DrawLine($pen,$pC,$pD)
      $g.DrawLine([System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(220,30,150,90),1.5),$pB,$pC)
    }else{$g.DrawLine($pen,$p1,$p2)}
  }else{$g.DrawLine($pen,$p1,$p2)}
  $midX=($a[0]+$z[0])/2;$midY=($a[1]+$z[1])/2
  $g.DrawString([string]$i,[System.Drawing.Font]::new('Arial',8,[System.Drawing.FontStyle]::Bold),[System.Drawing.Brushes]::DarkMagenta,[single]$midX,[single]$midY)
}
$g.Dispose();$b.Save('audit\batch4_knoy\plan_trace_overlay.png',[System.Drawing.Imaging.ImageFormat]::Png);$b.Dispose()
