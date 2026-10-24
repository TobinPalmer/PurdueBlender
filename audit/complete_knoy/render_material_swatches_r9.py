import bpy, math
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/knoy_hall.blend'))
scene=bpy.context.scene
asset=bpy.data.collections.get('Asset_knoy_hall'); assert asset
# Render-only isolated swatches from the saved source materials; never save these objects into the asset.
preview=bpy.data.collections.new('TEMP_Knoy_Material_Swatches_R9'); scene.collection.children.link(preview)
def link(obj):
 for c in list(obj.users_collection): c.objects.unlink(obj)
 preview.objects.link(obj)
 return obj
names=['KNOY_Purdue_Red_Brick','KNOY_Precast_Concrete','KNOY_Dark_Tinted_Glass']
for i,name in enumerate(names):
 bpy.ops.mesh.primitive_cube_add(size=1.8, location=((i-1)*2.8,0,0.95))
 o=link(bpy.context.object); o.name='SWATCH_'+name
 o.data.materials.clear(); o.data.materials.append(bpy.data.materials[name])
 # Apply small bevels to read the surfaces, as temporary presentation geometry.
 mod=o.modifiers.new('render-only edge highlight','BEVEL'); mod.width=0.04; mod.segments=3
 mod2=o.modifiers.new('render-only normals','WEIGHTED_NORMAL')
# Neutral matte ground plane.
bpy.ops.mesh.primitive_plane_add(size=18, location=(0,0,-0.02)); link(bpy.context.object).name='TEMP_Ground'
mat=bpy.data.materials.new('TEMP_neutral_ground'); mat.diffuse_color=(0.15,0.17,0.19,1); bpy.context.object.data.materials.append(mat)
# Lit backdrop/world.
world=scene.world or bpy.data.worlds.new('TEMP_world'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.22,0.25,0.29,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.5
bpy.ops.object.light_add(type='AREA', location=(0,-4,8)); light=link(bpy.context.object);light.name='TEMP_Key';light.data.energy=1200;light.data.shape='DISK';light.data.size=7
bpy.ops.object.light_add(type='AREA', location=(5,1,5)); fill=link(bpy.context.object);fill.name='TEMP_Fill';fill.data.energy=450;fill.data.size=5
bpy.ops.object.camera_add(location=(0,-12,4)); cam=link(bpy.context.object);cam.name='TEMP_Camera'; target=Vector((0,0,0.9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.7;scene.camera=cam
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1400;scene.render.resolution_y=780;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'audit/complete_knoy/knoy_facade_material_swatches_r9.png')
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False
bpy.ops.render.render(write_still=True)
print('render-only objects created; source asset not saved')

