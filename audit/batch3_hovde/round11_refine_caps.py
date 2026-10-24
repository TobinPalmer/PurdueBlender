import bpy, math
from pathlib import Path
from mathutils import Vector
PROJECT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=PROJECT/'modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
collection=bpy.data.collections['Asset_hovde_hall']; root=bpy.data.objects['HOVD_Root']
trim=bpy.data.materials['Hovde_Limestone_Trim']
for o in list(bpy.data.objects):
 if o.name.startswith('HOVD_R11_Corinthian_Acanthus_Leaves_'):
  mesh=o.data; bpy.data.objects.remove(o,do_unlink=True)
  if mesh and mesh.users==0: bpy.data.meshes.remove(mesh)
def add_leaf(v,f,x_face,yc,zc,width,height):
 levels=(0.0,.10,.24,.42,.58,.74,.88,1.0); widths=(.38,.54,.79,1.0,.94,.79,.53,.01); rows=len(levels); cols=3; start=len(v)
 front=[]; back=[]
 for t,wf in zip(levels,widths):
  z=zc+(t-.5)*height
  half=width*wf*.5
  for k in (-1,0,1):
   # Broader pointed blade, subtle sinuous edges, and a strong raised central rib.
   y=yc+k*half + (0.014*math.sin(t*math.pi*2) if k else 0)
   ridge=(.115 if k==0 else -.008)+.014*math.sin(math.pi*t)
   front.append((x_face+ridge,y,z)); back.append((x_face-.045,y,z))
 v.extend(front); v.extend(back); fs=start; bs=fs+rows*cols
 for j in range(rows-1):
  for k in range(cols-1):
   a=fs+j*cols+k; f.append((a,a+1,a+cols+1,a+cols))
   a=bs+j*cols+k; f.append((a,a+cols,a+cols+1,a+1))
 for j in range(rows-1):
  for k in (0,cols-1):
   a=fs+j*cols+k; b=bs+j*cols+k; f.append((a,b,b+cols,a+cols))
 for k in range(cols-1):
  for j in (0,rows-1):
   a=fs+j*cols+k; b=bs+j*cols+k; f.append((a,a+1,b+1,b))
for i in range(1,7):
 shaft=bpy.data.objects[f'HOVD_Classical_Column_{i}']; x,y=shaft.location.x,shaft.location.y
 verts=[]; faces=[]; face=x+.72
 for zc,spread,w,h in ((10.39,.31,.22,.28),(10.50,.28,.17,.22)):
  for dy in (-spread,0,spread): add_leaf(verts,faces,face,y+dy,zc,w,h)
 me=bpy.data.meshes.new(f'HOVD_R11_AcanthusMesh_{i}'); me.from_pydata(verts,[],faces); me.update(); me.materials.append(trim)
 for p in me.polygons:p.use_smooth=True
 ob=bpy.data.objects.new(f'HOVD_R11_Corinthian_Acanthus_Leaves_{i}',me); collection.objects.link(ob); ob.parent=root
 ob.location=(0,0,0)
bpy.context.view_layer.update(); bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
print('Refined six capitals with larger, pointed, visibly ribbed limestone leaf blades; no transform changes.')


