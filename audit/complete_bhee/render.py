import bpy, math
from pathlib import Path
from mathutils import Vector

D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_bhee')
P=D.parents[1]/'modular/buildings/electrical_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
camdata=bpy.data.cameras.new('BHEE_ReviewCamera');cam=bpy.data.objects.new('BHEE_ReviewCamera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO'
def render(name,loc,target,scale,res=(1600,1200),cutaway=False):
 scene.render.resolution_x,scene.render.resolution_y=res;cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
 hidden=[]
 if cutaway:
  prefixes=('BHEE_Spandrel','BHEE_Jamb','BHEE_Window','BHEE_Mullion','BHEE_WindowRail','BHEE_StoneSill','BHEE_StoneCourse','BHEE_Pier','BHEE_Courtyard','BHEE_InscriptionBand','BHEE_ElectricalEngineeringInscription','BHEE_FrontPortal','BHEE_FrontTileEave','BHEE_FrontDarkCornice')
  for ob in bpy.data.objects:
   slab_above_first=(ob.type=='MESH' and ob.name.startswith('BHEE_ClippedSlabFID') and min((ob.matrix_world@Vector(corner)).z for corner in ob.bound_box)>4.5)
   if ob.name.startswith(prefixes) or slab_above_first:
    hidden.append((ob,ob.hide_render,ob.hide_get()));ob.hide_render=True;ob.hide_set(True)
 scene.render.filepath=str(D/name);bpy.ops.render.render(write_still=True)
 for ob,hr,hs in hidden:ob.hide_render=hr;ob.hide_set(hs)

# Broad massing and footprint context.
render('overview_20261027.png',(120,130,120),(4,2,5),150)
# Elevation tied to the south front segment in official FID 292 footprint.
target=Vector((37,-39,9));out=Vector((.634,-.773,0));render('front_facade_20261027.png',target+out*62,target,58,(1800,1000))
# First-floor plan and furnishings, with exterior wall/roof geometry hidden for a readable review.
render('interior_cutaway_20261027.png',(60,80,110),(0,0,0),145,(1600,1200),True)

# Shaded facade detail to inspect the portable procedural masonry/glazing materials.
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.view_settings.view_transform='AgX'
if scene.world is None:scene.world=bpy.data.worlds.new('BHEE_ReviewWorld')
scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.22,.28,.38,1);bg.inputs['Strength'].default_value=.35
def area_light(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
 ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(target-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area_light('BHEE_ReviewKey',target+out*28+Vector((0,0,20)),2600,24)
area_light('BHEE_ReviewFill',target-out*18+Vector((0,0,9)),1200,20)
render('shader_overview_20261027.png',target+out*62,target,45,(1800,1000))
