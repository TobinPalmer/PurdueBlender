import bpy,os,json
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap";ASSET=os.path.join(ROOT,'modular','buildings','purdue_memorial_union.blend');OUT=os.path.join(ROOT,'audit','purdue_memorial_union_refine','roof_union_test_r4.png')
bpy.ops.wm.open_mainfile(filepath=ASSET);scene=bpy.context.scene;col=bpy.data.collections['Asset_purdue_memorial_union']
names=['PMU_R3_Roof_West_Wing','PMU_R3_Roof_East_Wing','PMU_R3_Roof_North_Wing','PMU_R3_Roof_South_West','PMU_R3_Roof_South_East','PMU_R3_Roof_Dormer_1','PMU_R3_Roof_Dormer_2','PMU_R3_Roof_Dormer_3']
src=[bpy.data.objects[n] for n in names if bpy.data.objects.get(n)]
copies=[]
for i,o in enumerate(src):
 c=o.copy();c.data=o.data.copy();c.name=f'TMP_R4_union_{i}';scene.collection.objects.link(c);copies.append(c)
for o in src:o.hide_render=True
base=copies[0];base.hide_render=False
try:
 for other in copies[1:]:
  mod=base.modifiers.new('R4_ExactRoofUnion','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=other
  bpy.context.view_layer.objects.active=base;base.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.data.objects.remove(other,do_unlink=True)
 base.name='R4_RoofUnion_Test'
 base.data.validate(clean_customdata=True)
 print('BOOLEAN_UNION_OK',len(base.data.vertices),len(base.data.polygons))
except Exception as e:
 print('BOOLEAN_UNION_FAILED',repr(e))
world=scene.world or bpy.data.worlds.new('R4UnionTestWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.07,.075,.085,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
def point(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('R4UnionTestCamera');cam=bpy.data.objects.new('R4UnionTestCamera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=145;cam.location=(75,-150,60);point(cam,(0,-2,12))
for n,loc,power,size,color in [('key',(-60,-100,90),900,55,(1,.88,.75)),('fill',(80,-60,50),550,55,(.72,.82,1))]:
 d=bpy.data.lights.new('R4UnionTest_'+n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new('R4UnionTest_'+n,d);scene.collection.objects.link(o);o.location=loc;point(o,(0,-5,10))
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=24;scene.render.resolution_x=1300;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.render.filepath=OUT;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';bpy.ops.render.render(write_still=True)
