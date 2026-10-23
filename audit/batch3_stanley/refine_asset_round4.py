import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
root=bpy.data.objects['AssetRoot_stanley_coulter_hall'];port=bpy.data.collections['SC_Portico_and_Entrances']
def boxmesh(obj, boxes, material):
 verts=[];faces=[]
 for (x0,y0,z0),(x1,y1,z1) in boxes:
  n=len(verts);verts += [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
  faces += [tuple(n+i for i in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
 me=bpy.data.meshes.new(obj.name+'_FinalMesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update();old=obj.data;obj.data=me
 if old.users==0:bpy.data.meshes.remove(old)
stone=bpy.data.materials['Bedford_Indiana_Limestone']
frame=bpy.data.objects.get('SC_Portico_Rectangular_Stone_Portal_Surround')
if frame:
 boxmesh(frame,[((28.0,-6.05,2.05),(28.3,-5.72,7.55)),((28.0,-2.22,2.05),(28.3,-1.89,7.55)),((28.0,-6.05,7.18),(28.45,-1.89,7.55))],stone)
ent=bpy.data.objects['SC_Portico_Entablature']
boxmesh(ent,[((28.15,-6.12,7.10),(30.35,-1.82,7.65))],stone)
can=bpy.data.objects['SC_Portico_Flat_Stone_Canopy']
boxmesh(can,[((28.0,-6.25,7.65),(30.55,-1.69,7.92))],stone)
text=bpy.data.objects.get('SC_Portico_3D_Text')
if text:
 text.scale.x*=0.82
 mw=text.matrix_world.copy();mw.translation+=Vector((-0.55,0,-0.08));text.matrix_world=mw
# Save and preserve the GIS placement frame.
bpy.ops.wm.save_as_mainfile(filepath=p)
print('SAVED',p,'portal',frame.name if frame else None,'text scale',list(text.scale) if text else None)
