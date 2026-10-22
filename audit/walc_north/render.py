import bpy,json,pathlib,math
from mathutils import Vector
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');m=json.loads((P/'modular/manifest.json').read_text());refs=json.loads((P/'audit/official_building_references.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for id in ['hovde_hall','elliott_hall_of_music','bell_tower']:
 a=next(a for a in m['assets'] if a['id']==id)
 with bpy.data.libraries.load(str(P/'modular'/a['file']),link=False) as (src,dst):dst.collections=[a['collection']]
 col=dst.collections[0];o=bpy.data.objects.new(id,None);o.instance_type='COLLECTION';o.instance_collection=col;o.location=(*a['placement_origin_xy_m'],0);bpy.context.collection.objects.link(o)
for b in refs['buildings']:
 if b['code'] not in ['HOVD','ELLT','BELL']:continue
 for i,ring in enumerate(b['rings_xy_m']):
  cu=bpy.data.curves.new(b['code'],'CURVE');cu.dimensions='3D';cu.bevel_depth=.22;s=cu.splines.new('POLY');s.points.add(len(ring)-1)
  for p,xy in zip(s.points,ring):p.co=(*xy,70,1)
  ob=bpy.data.objects.new(b['code'],cu);bpy.context.collection.objects.link(ob);ob.color=(1,0,0,1)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=False;scene.display.shading.background_type='WORLD';scene.world.color=(.8,.8,.8)
bpy.ops.object.camera_add(location=(-90,55,250));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=190;scene.camera=cam;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.filepath=str(P/'audit/walc_north/before.png');bpy.ops.render.render(write_still=True)
