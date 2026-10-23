import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=P/'audit/next_math';c=bpy.data.collections['Asset_math_sciences'];s=bpy.context.scene
# Existing inherited shader colors are authoritative for viewport parity only.
parity=[]
for m in {sl.material for o in c.all_objects for sl in o.material_slots if sl.material}:
 if m.use_nodes:
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs and not bs.inputs['Base Color'].is_linked:
   color=tuple(bs.inputs['Base Color'].default_value)
   if max(abs(a-b) for a,b in zip(color,m.diffuse_color))>.001:m.diffuse_color=color;parity.append(m.name)
m=bpy.data.materials.new('MATH_Photo_Brick_Metre');m.use_nodes=True;m.diffuse_color=(.30,.16,.12,1);n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
uv=n.new('ShaderNodeTexCoord');brick=n.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.24;brick.inputs['Row Height'].default_value=.075;brick.inputs['Mortar Size'].default_value=.003;brick.inputs['Color1'].default_value=(.27,.135,.105,1);brick.inputs['Color2'].default_value=(.37,.22,.18,1);brick.inputs['Mortar'].default_value=(.35,.32,.28,1);l.new(uv.outputs['UV'],brick.inputs['Vector']);l.new(brick.outputs['Color'],bs.inputs['Base Color']);bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.002;bump.inputs['Strength'].default_value=.25;l.new(brick.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
changed=[]
for o in c.all_objects:
 if o.type!='MESH':continue
 if o.name=='MATH_Corrected_GIS_Wall_Envelope' or ('Corner_Tower' in o.name and 'Brick' in o.name):
  o.data.materials.clear();o.data.materials.append(m)
  uvdata=o.data.uv_layers.get('MATH_Physical_Metre') or o.data.uv_layers.new(name='MATH_Physical_Metre');o.data.uv_layers.active=uvdata
  for poly in o.data.polygons:
   poly.material_index=0
   for li in poly.loop_indices:
    co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
    uvdata.data[li].uv=((co.y if abs(poly.normal.x)>abs(poly.normal.y) else co.x),co.z)
  changed.append(o.name)
# Embedded procedural shader has no image files or external dependencies.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'modular/buildings/math_sciences.blend'));bpy.ops.wm.open_mainfile(filepath=str(P/'modular/buildings/math_sciences.blend'))
c=bpy.data.collections['Asset_math_sciences'];s=bpy.context.scene
camd=bpy.data.cameras.new('MathReview');cam=bpy.data.objects.new('MathReview',camd);s.collection.objects.link(cam);cam.location=(90,-110,65);cam.rotation_euler=(Vector((0,0,13))-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=110;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
sunD=bpy.data.lights.new('ReviewSun','SUN');sunD.energy=3;sun=bpy.data.objects.new('ReviewSun',sunD);s.collection.objects.link(sun);sun.rotation_euler=(.4,-.5,-.4)
s.world.color=(.3,.3,.3);s.render.filepath=str(D/'after.png');bpy.ops.render.render(write_still=True)
D.joinpath('changes.json').write_text(json.dumps({'count':len(c.all_objects),'materials_parity_fixed':parity,'brick_assigned_objects':changed,'reopened':True,'geometry_changed':False,'source':'https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg','source_provider':'Purdue Department of Statistics','retrieved':'2026-10-22','photo_date':'unknown','source_CRS':'photograph, not georeferenced','uncertainty':'Photo supports reddish brick and pale window surrounds only. Exact brick dimensions/colors estimated. Heights and full facade arrangement remain unverified.'},indent=2))
