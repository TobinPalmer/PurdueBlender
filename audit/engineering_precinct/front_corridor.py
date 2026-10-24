import bpy, math
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
cam=(21.7115,193.0986); f=(-39.6,97.8); dx=f[0]-cam[0]; dy=f[1]-cam[1]; n=math.hypot(dx,dy); ux,uy=dx/n,dy/n
for o in bpy.data.objects:
 if not o.name.startswith('Plant_'): continue
 vx=o.location.x-cam[0]; vy=o.location.y-cam[1]; along=vx*ux+vy*uy; perp=vx*(-uy)+vy*ux
 x=o.get('reference_crown_x',9); y=o.get('reference_crown_y',9)
 if 0<along<120 and abs(perp)<35:
  print(o.name, 'depth',round(along,1),'side',round(perp,1),'screen',round(x,2),round(y,2),'spread',o.get('inventory_spread_ft'))
