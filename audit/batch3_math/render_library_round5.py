import bpy
from pathlib import Path
from mathutils import Vector
root=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); out=root/'audit/batch3_math'
asset=bpy.data.collections['Asset_math_sciences']
sc=bpy.data.scenes.new('Math Third Floor Library Round 5 Cutaway')
coll=bpy.data.collections.new('Round 5 plan review selection'); sc.collection.children.link(coll)
keep=set()
for o in asset.all_objects:
 if not o: continue
 n=o.name
 include=(n in keep or (n.startswith('MATH_2026_Library_') and n!='MATH_2026_Library_Circulation_Inlay') or n.startswith('MATH_2026_Inferred_Group_Room_'))
 if include:
  coll.objects.link(o)
  low=n.lower()
  if 'boundar' in low or 'partition' in low or 'frame' in low: o.color=(.19,.25,.28,1)
  elif 'group_room_glaz' in low or 'door' in low: o.color=(.25,.58,.67,1)
  elif 'book_spines' in low: o.color=(.70,.34,.20,1)
  elif 'bookcase' in low: o.color=(.47,.29,.15,1)
  elif 'chair' in low or 'seat' in low: o.color=(.72,.47,.28,1)
  elif 'table' in low or 'carrel' in low: o.color=(.62,.38,.19,1)
  elif 'floor' in low or 'carpet' in low or 'inlay' in low or 'border' in low: o.color=(.87,.82,.70,1)
  else: o.color=(.73,.70,.63,1)
# Use a dedicated neutral floor in the evidence scene; avoid legacy shell/ceiling occlusion.\nmesh=bpy.data.meshes.new('Review floor mesh')\nmesh.from_pydata([(-10,5,10.63),(10,5,10.63),(10,27,10.63),(-10,27,10.63)],[],[(0,1,2,3)])\nfloor=bpy.data.objects.new('Review floor 20x22m',mesh); sc.collection.objects.link(floor); floor.color=(.87,.82,.70,1)\n# Remove 3D perimeter walls from this review scene only, while keeping saved model intact.
for name in ['MATH_Lib_Wall_East','MATH_Lib_Wall_South','MATH_Lib_Wall_North']:
 o=bpy.data.objects.get(name)
 if o and o.name in coll.objects: coll.objects.unlink(o)
sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.light='STUDIO'; sc.display.shading.color_type='OBJECT'; sc.display.shading.show_shadows=False; sc.display.shading.show_cavity=True; sc.display.shading.cavity_type='WORLD'; sc.display.shading.curvature_ridge_factor=1.25; sc.display.shading.curvature_valley_factor=1.0; sc.display.shading.background_type='WORLD'; sc.world=bpy.data.worlds.new('Round 5 plan world'); sc.world.color=(.96,.96,.96)
camd=bpy.data.cameras.new('Library plan camera r5'); camd.type='ORTHO'; camd.ortho_scale=23.5; cam=bpy.data.objects.new('Library plan camera r5',camd); sc.collection.objects.link(cam); cam.location=(.5,17.1,42); cam.rotation_euler=(Vector((.5,17.1,10.6))-cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
for label,x,y in [('311.3',-8.25,14.5),('311.4',-4.0,15.55),('311.5',1.8,15.55),('311.7',6.2,15.55),('311.8',9.0,14.5)]:
 d=bpy.data.curves.new('Plan zone '+label,'FONT'); d.body=label; d.size=.42; o=bpy.data.objects.new('Plan zone '+label,d); sc.collection.objects.link(o); o.location=(x,y,16.2); o.color=(.025,.04,.05,1)
sc.render.resolution_x=1600; sc.render.resolution_y=1600; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(out/'library_cutaway_round5.png')
bpy.context.window.scene=sc; bpy.ops.render.render(write_still=True); print('round5 focused library objects',len(coll.objects))


