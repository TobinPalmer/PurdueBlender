import bpy, os, math
from mathutils import Vector
ROOT=os.path.abspath('.'); OUT=os.path.join(ROOT,'audit','texture_final_two')

def coll_visible(o): return not any(c.hide_render for c in o.users_collection)
def bounds(objs):
 pts=[]
 for o in objs:
  if o.type!='MESH' or o.hide_render or not coll_visible(o): continue
  pts.extend(o.matrix_world@Vector(c) for c in o.bound_box)
 if not pts: return None
 mn=Vector(tuple(min(p[i] for p in pts) for i in range(3))); mx=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
 return mn,mx,(mn+mx)*.5,mx-mn

def render(tag,objs,path,zoom=False):
 b=bounds(objs)
 if not b: print('NO OBJECTS',tag); return
 mn,mx,c,d=b; span=max(d.x,d.y,d.z)
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='LIGHT': o.hide_render=True
 camd=bpy.data.cameras.new('Texture QA '+tag); cam=bpy.data.objects.new('Texture QA '+tag,camd); scene.collection.objects.link(cam)
 if zoom:
  # Constrain the roof close-up to its target roof planes, not adjacent site geometry.
  cam.location=c+Vector((span*.72,-span*.98,span*1.1)); camd.type='ORTHO'; camd.ortho_scale=max(d.x,d.y)*1.08
 else:
  cam.location=c+Vector((span*1.0,-span*1.4,span*1.02)); camd.type='ORTHO'; camd.ortho_scale=span*1.28
 cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler(); scene.camera=cam
 if not scene.world: scene.world=bpy.data.worlds.new('Texture QA World')
 scene.world.use_nodes=True; bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.24,.30,.38,1); bg.inputs['Strength'].default_value=.62
 ld=bpy.data.lights.new('Texture QA Sun','SUN'); lo=bpy.data.objects.new('Texture QA Sun',ld); scene.collection.objects.link(lo); lo.rotation_euler=(math.radians(24),math.radians(-18),math.radians(-35)); ld.energy=3.1; ld.angle=math.radians(18)
 scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=850; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=path
 scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=.25; scene.view_settings.gamma=1
 print('BOUNDS',tag,tuple(round(v,2) for v in d),'target objects',len(objs),'camera scale',camd.ortho_scale)
 bpy.ops.render.render(write_still=True)

for key in ('mccutcheon_hall','niswonger_aviation_tech'):
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings',key+'.blend'))
 meshes=[o for o in bpy.data.objects if o.type=='MESH' and coll_visible(o) and not o.hide_render]
 primary=[o for o in meshes if not any(t in o.name.lower() for t in ('site_','ground_', 'tree_', 'shrubs'))]
 render(key+' overview',primary or meshes,os.path.join(OUT,key+'_overview.png'))
 roofs=[o for o in meshes if any(t in o.name.lower() for t in ('roof_membrane','roof_','standingseam','rtu_unit'))]
 render(key+' roof close',roofs or primary or meshes,os.path.join(OUT,key+'_roof_close.png'),True)
