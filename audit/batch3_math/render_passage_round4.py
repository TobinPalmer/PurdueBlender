import bpy
from pathlib import Path
from mathutils import Vector
root=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
src=root/'modular/buildings/math_sciences.blend'; out=root/'audit/batch3_math'
bpy.ops.wm.open_mainfile(filepath=str(src))
asset=bpy.data.collections['Asset_math_sciences']
sc=bpy.data.scenes.new('Math Ground Level Passage Source Review')
sc.collection.children.link(asset)
sc.render.engine='CYCLES'; sc.cycles.samples=32
sc.render.resolution_x=1500; sc.render.resolution_y=950; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'; sc.view_settings.exposure=.45
sc.world=bpy.data.worlds.new('Math Passage Review World'); sc.world.use_nodes=True
sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.56,.59,.62,1)
sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.8
# Neutral sun and broad fill reveal the sheltered opening without adding any new building geometry.
sun_data=bpy.data.lights.new('Passage daylight','SUN'); sun_data.energy=2.0; sun_data.angle=.25
sun=bpy.data.objects.new('Passage daylight',sun_data); sc.collection.objects.link(sun); sun.rotation_euler=(.25,-.4,-.6)
fill_data=bpy.data.lights.new('Passage soft fill','AREA'); fill_data.energy=5000; fill_data.shape='DISK'; fill_data.size=28
fill=bpy.data.objects.new('Passage soft fill',fill_data); sc.collection.objects.link(fill); fill.location=(30,-28,18); fill.rotation_euler=(Vector((0,0,5))-fill.location).to_track_quat('-Z','Y').to_euler()
mesh=bpy.data.meshes.new('Passage ground mesh'); mesh.from_pydata([(-120,-120,-.08),(120,-120,-.08),(120,120,-.08),(-120,120,-.08)],[],[(0,1,2,3)])
g=bpy.data.objects.new('Passage ground',mesh); sc.collection.objects.link(g); m=bpy.data.materials.new('Neutral ground'); m.diffuse_color=(.39,.42,.43,1); m.use_nodes=True; next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.39,.42,.43,1); g.data.materials.append(m)
cd=bpy.data.cameras.new('Passage eye camera'); cd.lens=32
cam=bpy.data.objects.new('Passage eye camera',cd); sc.collection.objects.link(cam)
cam.location=(52,-4,2.4); target=Vector((0,-4,5.2)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
sc.render.filepath=str(out/'passage_round4.png')
bpy.context.window.scene=sc; bpy.ops.render.render(write_still=True)
print('rendered passage view from reopened saved file')
