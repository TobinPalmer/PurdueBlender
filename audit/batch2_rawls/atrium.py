import bpy,os,math
from mathutils import Vector
col=bpy.data.collections['Asset_rawls_hall'];ox=323.6582336425781;oy=-409.62242126464844
def box(n,x,y,z,dx,dy,dz,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x-ox,y-oy,z));o=bpy.context.object;o.name='RAWL_2026_'+n;o.dimensions=(dx,dy,dz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
 if mat:o.data.materials.append(mat)
 o['evidence']='2024 published firstfloor corridor plan + 2003 archival atrium photograph; dimensions estimated';return o
con=bpy.data.materials['RAWL_Concrete_Floor'];wood=bpy.data.materials['RAWL_Interior_Wood'];gold=bpy.data.materials['RAWL_Interior_Ochre'];glass=bpy.data.materials['RAWL_CurtainWall_Glass'];carpet=bpy.data.materials['RAWL_Interior_CharcoalCarpet']
# Repair guessed old slab void and cut a corridor-registered opening.
ground=bpy.data.objects['RAWL_FloorSlab_L1_Ground']
cutter=box('TempAtriumCut',331,-394.25,13,32,5.5,26,None)
for n,z in [('L2',5.486),('L3',10.577),('L4',15.667),('L5',20.33)]:
 o=bpy.data.objects['RAWL_FloorSlab_'+n];old=o.data;o.data=ground.data.copy()
 for v in o.data.vertices:v.co.z+=z
 mod=o.modifiers.new('PublishedCorridorAtrium','BOOLEAN');mod.object=cutter;mod.operation='DIFFERENCE';bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)
for n in ['RAWL_Atrium_Mezzanine_Balustrades','RAWL_Atrium_Structural_Columns']:
 o=bpy.data.objects.get(n)
 if o:
  for c in list(o.users_collection):c.objects.unlink(o)
  ref=bpy.data.collections.get('RAWL_Previous_Atrium_Reference')
  if not ref:ref=bpy.data.collections.new('RAWL_Previous_Atrium_Reference')
  ref.objects.link(o)
for z in [5.486,10.577,15.667]:
 for y in [-397,-391.5]:
  box('AtriumGlassRail',331,y,z+.52,32,.045,1.04,glass);box('AtriumWoodHandrail',331,y,z+1.08,32,.07,.06,wood)
 for x in [320,343]:
  box('AtriumBridge',x,-394.25,z-.12,2.1,5.5,.24,con)
  for xx in [x-1.05,x+1.05]:box('BridgeWoodRail',xx,-394.25,z+1.08,.07,5.5,.06,wood);box('BridgeGlassRail',xx,-394.25,z+.52,.045,5.5,1.04,glass)
# Broad straight public flight observed in historical and Nov2024 photos.
for i in range(32):
 x=320+i*.28;h=(i+1)*5.486/32
 box('AtriumStair',x,-398.0,h/2,.29,2.0,h,carpet)
for x in [319,327,335,343]:box('OchreAtriumPier',x,-398.8,7.7,.5,.4,15.4,gold)
text=bpy.data.texts['RAWL_2026_EVIDENCE'];text.write('\nIteration: original guessed central atrium archived; slabs recut along public northcorridor from registered published plan; glassrails woodhandrails transversebridges broadstraightstairs added from photo. Exact width, spans, stairs, elevations estimates; roofs still inherited.')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
# Shader view of actual interior with upper slabs/roof excluded only from render to show new void.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=1100;s.render.resolution_y=750;s.render.resolution_percentage=100
for o in bpy.data.objects:
 if o and o.type=='LIGHT':o.hide_render=True
 if o and ('Roof' in o.name or 'Skylight' in o.name or 'FloorSlab_L5' in o.name):o.hide_render=True
w=bpy.data.worlds.new('AtriumReviewWorld');s.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[1].default_value=.9
ld=bpy.data.lights.new('AtriumReviewLight','AREA');ld.energy=7000;ld.shape='DISK';ld.size=20;lo=bpy.data.objects.new('AtriumReviewLight',ld);s.collection.objects.link(lo);lo.location=(331-ox,-394-oy,22)
cam=bpy.data.objects.new('AtriumReviewCam',bpy.data.cameras.new('AtriumReviewCam'));s.collection.objects.link(cam);cam.location=(314-ox,-394.3-oy,2);cam.rotation_euler=(Vector((344-ox,-394.3-oy,7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=18;s.camera=cam;s.render.filepath=os.path.join(os.path.dirname(__file__),'atrium.png');bpy.ops.render.render(write_still=True)
