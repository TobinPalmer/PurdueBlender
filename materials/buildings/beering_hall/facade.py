import bpy,math,os
from mathutils import Vector
R=os.path.abspath('.');c=bpy.data.collections['Asset_beering_hall'];s=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'materials/buildings/beering_hall/materials_only_backup.blend'),copy=True)
glass=bpy.data.materials['Beering_Solar_Ribbon_Glass'];p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Transmission Weight'].default_value=0;p.inputs['Base Color'].default_value=(.025,.055,.08,1);p.inputs['Metallic'].default_value=.25;p.inputs['Roughness'].default_value=.17
metal=bpy.data.materials['Beering_Architectural_Bronze_Metal']
def box(name,loc,dims,mat):
 x,y,z=(d*.5 for d in dims);mesh=bpy.data.meshes.new(name);mesh.from_pydata([(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)],[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);mesh.materials.append(mat);o=bpy.data.objects.new(name,mesh);c.objects.link(o);o.location=loc;return o
# Representative repeated glazing arrangement for previously blank tower elevations.
count=0
for side,coord,positions in [('W',-6.78,[8.0,14.5,21,27.5,34]),('E',39.08,[8.0,14.5,21,27.5,34]),('S',3.02,[-2,5,12,19,26,33]),('N',41.28,[-2,5,12,19,26,33])]:
 for row,z in enumerate([3,7,11,15,19,23]):
  for j,u in enumerate(positions):
   alongx=side in 'SN';loc=(u,coord,z) if alongx else (coord,u,z);dim=(1.75,.14,2.15) if alongx else (.14,1.75,2.15)
   o=box('BRNG_PBR_Tower_Window_'+side+f'_{row}_{j}',loc,dim,glass);count+=1
   for offset in [-.92,.92]:
    a=list(loc);a[0 if alongx else 1]+=offset;box(o.name+'_Jamb'+str(offset),a,(.08,.2,2.3) if alongx else (.2,.08,2.3),metal)
   for offset in [-1.12,1.12]:
    a=list(loc);a[2]+=offset;box(o.name+'_Rail'+str(offset),a,(1.92,.2,.08) if alongx else (.2,1.92,.08),metal)
# Add east classroom-window rhythm, matching existing west window source proportions, missing in inherited model.
for z in [2.5,6.5,10.5]:
 for j,y in enumerate([-27,-22,-17,-12,-7,-2,3,8,13,18,23,28,33]):
  box('BRNG_PBR_Classroom_East_'+str(z)+'_'+str(j),(-6.53,y,z),(.14,3.2,1.8),glass);count+=1
# Non-destructive small bevel highlights on three original masonry cores only.
for o in c.all_objects:
 if o.type=='MESH' and 'Masonry' in o.name:
  b=o.modifiers.new('PBR masonry edge highlights','BEVEL');b.width=.035;b.segments=2
s.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'modular/buildings/beering_hall.blend'))
s.render.filepath=os.path.join(R,'materials/buildings/beering_hall/hero.png');bpy.ops.render.render(write_still=True)
cam=s.camera;cam.location=(-50,-42,9);cam.rotation_euler=(Vector((-36,-22,7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=54
s.render.filepath=os.path.join(R,'materials/buildings/beering_hall/closeup.png');bpy.ops.render.render(write_still=True)
print('NEW PANES',count,'TOTAL',len(c.all_objects))
