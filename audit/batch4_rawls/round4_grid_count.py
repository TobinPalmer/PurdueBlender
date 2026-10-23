import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');g=bpy.data.objects['RAWL_North_Windows_Glass'];hs=[]
for p in g.data.polygons:
 pts=[g.matrix_world@g.data.vertices[i].co for i in p.vertices];hs.append((min(v.x for v in pts)-.055,max(v.x for v in pts)+.055,min(v.z for v in pts)-.035,max(v.z for v in pts)+.035))
print('bounds',hs[:3],hs[-3:]);xs=sorted(set([-21.394,33.333]+[round(v,5) for h in hs for v in h[:2]]));zs=sorted(set([1.5,24.08]+[round(v,5) for h in hs for v in h[2:]]));print('counts',len(xs),len(zs));skip=0;keep=0;holecenters=[]
for x0,x1 in zip(xs,xs[1:]):
 for z0,z1 in zip(zs,zs[1:]):
  cx=(x0+x1)/2;cz=(z0+z1)/2
  if any(h[0]-1e-4<cx<h[1]+1e-4 and h[2]-1e-4<cz<h[3]+1e-4 for h in hs):skip+=1;holecenters.append((cx,cz))
  else:keep+=1
print('skip keep',skip,keep,'centers',holecenters[:4])
