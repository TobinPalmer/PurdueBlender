import bpy,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene;wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];glass=bpy.data.objects['RAWL_North_Windows_Glass'];verts=[];faces=[]
for poly in glass.data.polygons:
 pts=[glass.matrix_world@glass.data.vertices[i].co for i in poly.vertices]
 if len(pts)!=4:continue
 cx=sum(v.x for v in pts)/4;cz=sum(v.z for v in pts)/4;front=[]
 for v in pts:
  side=-1 if v.x<cx else 1;top=-1 if v.z<cz else 1;x=v.x+side*.08;z=v.z+top*.08;y=v.y+(x-v.x)*(.597/54.727);front.append(Vector((x,y+.04,z)))
 back=[v+Vector((0,-1.5,0)) for v in front];base=len(verts);verts += [tuple(v) for v in front+back];faces += [tuple(base+i for i in [0,1,2,3]),tuple(base+i for i in [7,6,5,4])]
 for i in range(4):faces.append((base+i,base+i+4,base+((i+1)%4+4),base+(i+1)%4))
me=bpy.data.meshes.new('R4C');me.from_pydata(verts,[],faces);me.update();cut=bpy.data.objects.new('R4C',me);s.collection.objects.link(cut);dup=wall.copy();dup.data=wall.data.copy();dup.name='WallCut';s.collection.objects.link(dup);dup.hide_render=False;wall.hide_render=True;wall.hide_viewport=True
mod=dup.modifiers.new('cut','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=dup;dup.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);cut.hide_render=True
s.view_layers[0].update();dg=bpy.context.evaluated_depsgraph_get()
for x,z in [(25,2.4),(25,5.2),(25,8),(5,2.4),(5,5.2),(5,8)]:
 hit,loc,n,fi,obj,mat=s.ray_cast(dg,Vector((x,30,z)),Vector((0,-1,0)),distance=30);print('ray',x,z,hit,obj.name if obj else None,tuple(round(v,3) for v in loc))
print('wall faces',len(wall.data.polygons),len(dup.data.polygons))
