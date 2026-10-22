import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');sys.path.insert(0,str(R/'materials/buildings/armory'));from secondary import aim
col=bpy.data.collections['Asset_armory'];root=bpy.data.objects.get('Armory_Root');brick=bpy.data.materials['Purdue_Red_Brick'];stone=bpy.data.materials['Bedford_Indiana_Limestone']
# Existing roof slabs remain recoverable but render a continuous interpolated roof skin instead.
segs=sorted([o for o in col.all_objects if o.name.startswith('Armory_Roof_Seg_')],key=lambda o:o.location.x)
xs=[segs[0].location.x-segs[0].dimensions.x/2]+[o.location.x for o in segs]+[segs[-1].location.x+segs[-1].dimensions.x/2]
zs=[segs[0].location.z+.2]+[o.location.z+.2 for o in segs]+[segs[-1].location.z+.2]
verts=[]
for x,z in zip(xs,zs):verts.extend([(x,-43.75,z),(x,43.75,z)])
faces=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(xs)-1)]
me=bpy.data.meshes.new('Continuous_Roof_Skin');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Armory_Continuous_Roof_Repair',me);col.objects.link(o);o.data.materials.append(bpy.data.materials['Armory_Roof_Copper']);sol=o.modifiers.new('Roof thickness','SOLIDIFY');sol.thickness=.25
for x in segs:x.hide_render=True;x.hide_viewport=True
# Coplanar tower and main wall surfaces caused black rectangles.
for o in col.all_objects:
 if o.name.startswith('Armory_Tower_Shaft_'):
  for v in o.data.vertices:
   if v.co.x*o.location.x>0:v.co.x+=.015*(1 if o.location.x>0 else -1)/o.scale.x
   if v.co.y*o.location.y>0:v.co.y+=.015*(1 if o.location.y>0 else -1)/o.scale.y
# Exterior window glass boxes were buried in walls: expose existing panel fronts and add industrial pale mullions.
glass=bpy.data.materials['Solar_Ribbon_Glass'];p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.035,.052,.068,1);p.inputs['Transmission Weight'].default_value=.04;p.inputs['Metallic'].default_value=.25;p.inputs['Roughness'].default_value=.19
frame=bpy.data.materials.new('Armory_Painted_Window_Frames');frame.diffuse_color=(.6,.63,.61,1);frame.use_nodes=True;bs=frame.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.6,.63,.61,1);bs.inputs['Roughness'].default_value=.42
count=0
for o in list(col.all_objects):
 if not (o.name.startswith('Armory_Window_East') or o.name.startswith('Armory_Window_West')):continue
 sg=1 if o.location.x>0 else -1;o.location.x=sg*25.80
 # pale perimeter and cross muntins on actual existing window size, no new bays invented
 w,h=o.dimensions.y,o.dimensions.z
 for dy,dz,wy,hz in [(-w/2,0,.07,h),(w/2,0,.07,h),(0,-h/2,w,.07),(0,h/2,w,.07),(0,0,.045,h),(0,0,w,.045)]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(sg*25.98,o.location.y+dy,o.location.z+dz));f=bpy.context.object;f.name='Armory_Window_Frame_Repair';f.dimensions=(.07,wy,hz)
  for c in list(f.users_collection):c.objects.unlink(f)
  col.objects.link(f);f.data.materials.append(frame);count+=1
s=bpy.context.scene;cam=s.camera;aim(cam,(112,-135,70),(0,0,8),48);bpy.ops.wm.save_as_mainfile(filepath=str(R/'modular/buildings/armory.blend'));bpy.ops.wm.open_mainfile(filepath=str(R/'modular/buildings/armory.blend'));s=bpy.context.scene;cam=s.camera
s.render.filepath=str(R/'materials/buildings/armory/hero.png');bpy.ops.render.render(write_still=True)
aim(cam,(38,-29,7),(24.5,-22,6.5),55);s.render.filepath=str(R/'materials/buildings/armory/closeup.png');bpy.ops.render.render(write_still=True)
print('FINAL_COUNTS',len(bpy.data.collections['Asset_armory'].all_objects),count)
