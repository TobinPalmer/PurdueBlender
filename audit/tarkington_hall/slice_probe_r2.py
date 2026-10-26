exec(open('audit/tarkington_hall/slice_probe_r1.py').read().split('for lo,hi')[0])
for y in [18,20,24,28,32,36,40,44,48,52,56,60,63,-8,-12,-16,-20,-24,-28,-32,-36,-40,-44,-48,-52]:
 s=g.intersection(box(-100,y-.25,100,y+.25))
 print(y,[(round(a.bounds[0],1),round(a.bounds[2],1),round(a.bounds[1],1),round(a.bounds[3],1)) for a in (s.geoms if hasattr(s,'geoms') else [s]) if a.area>0])
