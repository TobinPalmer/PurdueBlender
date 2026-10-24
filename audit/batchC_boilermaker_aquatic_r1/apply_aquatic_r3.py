import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend'; AUD=ROOT/'audit/batchC_boilermaker_aquatic_r1'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
asset=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']; facade=bpy.data.collections['AQUA_Facade']; interior=bpy.data.collections['AQUA_Interior']; roof=bpy.data.collections['AQUA_Roof']; structure=bpy.data.collections['AQUA_Structure']; rig=bpy.data.collections['Preview_Rig']
brick=bpy.data.materials['AQUA | mottled Purdue red-brown brick']; stone=bpy.data.materials['AQUA | warm gray limestone / precast']; metal=bpy.data.materials['AQUA | charcoal anodized metal']; roofmat=bpy.data.materials['AQUA | weathered membrane / standing seam']
# Replace generic noise-only brick appearance with a real-scale procedural running bond.
brick.use_nodes=True; nt=brick.node_tree; nodes=nt.nodes; links=nt.links; bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
coord=nodes.get('Texture Coordinate') or nodes.new('ShaderNodeTexCoord'); tex=nodes.new('ShaderNodeTexBrick'); tex.inputs['Scale'].default_value=1.0; tex.inputs['Brick Width'].default_value=.68; tex.inputs['Row Height'].default_value=.24; tex.inputs['Mortar Size'].default_value=.018; tex.inputs['Mortar Smooth'].default_value=.06; tex.inputs['Color1'].default_value=(.40,.135,.075,1); tex.inputs['Color2'].default_value=(.29,.082,.045,1); tex.inputs['Mortar'].default_value=(.17,.15,.13,1)
links.new(coord.outputs['Object'],tex.inputs['Vector']); links.new(tex.outputs['Color'],bs.inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=4.5; noise.inputs['Detail'].default_value=2.0; bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.11; bump.inputs['Distance'].default_value=.018; links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],bs.inputs['Normal']); bs.inputs['Roughness'].default_value=.82
# Slightly more legible low-sheen roof metal with microtexture; roof section stays uncertain.
roofmat.use_nodes=True; rn=roofmat.node_tree.nodes; rl=roofmat.node_tree.links; rbs=next(n for n in rn if n.type=='BSDF_PRINCIPLED'); rbs.inputs['Base Color'].default_value=(.23,.25,.26,1); rbs.inputs['Metallic'].default_value=.34; rbs.inputs['Roughness'].default_value=.58
rnoise=rn.new('ShaderNodeTexNoise'); rnoise.inputs['Scale'].default_value=34.; rnoise.inputs['Detail'].default_value=2.; rb=rn.new('ShaderNodeBump'); rb.inputs['Strength'].default_value=.13; rb.inputs['Distance'].default_value=.004; rl.new(rnoise.outputs['Fac'],rb.inputs['Height']); rl.new(rb.outputs['Normal'],rbs.inputs['Normal'])
# Scale down R2 masonry piers to a lighter articulation more like the narrow brick divisions in the street-level reference.
for o in list(asset.all_objects):
 if o.name.startswith('AQUA R2 | north brick pilaster'):
  o.dimensions=(.18,.14,8.05); bpy.context.view_layer.objects.active=o; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.name=o.name.replace('AQUA R2 |','AQUA R3 |')
# Remove the oversized sign board. Keep the observed centered wall lettering, scaled as a direct-mounted sign.
plaque=bpy.data.objects.get('AQUA R2 | north entrance dark sign plaque')
if plaque: bpy.data.objects.remove(plaque,do_unlink=True)
letter=bpy.data.objects['AQUA R1 | north facade building name']; letter.data.size=.47; letter.data.extrude=.012; letter.data.materials.clear()
white=bpy.data.materials.get('AQUA R3 | warm white exterior lettering') or bpy.data.materials.new('AQUA R3 | warm white exterior lettering'); white.diffuse_color=(.84,.82,.75,1); white.use_nodes=True; wbs=next(n for n in white.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); wbs.inputs['Base Color'].default_value=(.84,.82,.75,1); wbs.inputs['Roughness'].default_value=.58; letter.data.materials.append(white)
letter['source_note']='Name and location are visible in July 2023 Street View; type scale and direct-mount appearance are visual estimates, not measured dimensions.'
# Replace vague inherited roof ribs with understated standing-seam lines over the estimated shallow gable.
old=bpy.data.objects.get('AQUA | clear-span natatorium | standing seam roof ribs')
if old: bpy.data.objects.remove(old,do_unlink=True)
curve=bpy.data.curves.new('AQUA R3 | roof standing seam panel joints','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.014; curve.bevel_resolution=1
for y in [ -50.0+i*2.4 for i in range(43) ]:
 for side in (-1,1):
  sp=curve.splines.new('POLY'); sp.points.add(2)
  for idx,x in enumerate((0.,side*15.2,side*30.45)):
   z=12.2-3.0*abs(x)/30.45+.025; sp.points[idx].co=(x,y,z,1)
seams=bpy.data.objects.new('AQUA R3 | subtle standing seams on estimated roof',curve); roof.objects.link(seams); curve.materials.append(metal); seams['geometry_status']='Visual standing-seam panel rhythm; roof profile and exact spacing are estimates because no roof section was found.'
# Rebuild schematic mezzanine stairs to meet the gallery edge and show an explicit plausible circulation route.
for o in list(interior.objects):
 if o.name.startswith('AQUA R2 | schematic mezzanine stair tread') or o.name.startswith('AQUA R2 | mezzanine stair handrail'):
  bpy.data.objects.remove(o,do_unlink=True)
def cube(name,loc,size,mat,col):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection): c.objects.unlink(o)
 col.objects.link(o); o.data.materials.append(mat); return o
for run,y in enumerate((-17.0,17.0),1):
 for i in range(12):
  x=18.05+i*.46; z=.95+i*.30
  cube(f'AQUA R3 | schematic mezzanine stair {run} tread {i+1}',(x,y,z),(.50,1.10,.12),stone,interior)
 for side in (-1,1):
  c=bpy.data.curves.new(f'AQUA R3 | stair rail {run}_{side}','CURVE'); c.dimensions='3D'; c.bevel_depth=.035; c.bevel_resolution=2; s=c.splines.new('POLY'); s.points.add(1); s.points[0].co=(17.85,y+side*.66,1.8,1); s.points[1].co=(23.65,y+side*.66,5.05,1); ob=bpy.data.objects.new(f'AQUA R3 | mezzanine stair handrail {run}_{side}',c); interior.objects.link(ob); c.materials.append(metal)
# Add slim supports under the documented, schematically located gallery.
for i,y in enumerate((-19,-12,-5,5,12,19),1):
 if not bpy.data.objects.get(f'AQUA R3 | mezzanine support {i}'):
  cube(f'AQUA R3 | mezzanine support {i}',(24.45,y,2.65),(.16,.16,4.15),metal,interior)
# Camera for a grounded, full exterior view; a close facade detail remains available separately.
def camera(name,loc,target,lens,ortho=None):
 d=bpy.data.cameras.new(name); d.lens=lens
 if ortho is not None: d.type='ORTHO'; d.ortho_scale=ortho
 o=bpy.data.objects.new(name,d); rig.objects.link(o); o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); return o
for n in ('AQUA R3 | North Elevation Camera','AQUA R3 | Street Approach Camera','AQUA R3 | Interior Gallery Camera'):
 old=bpy.data.objects.get(n)
 if old: bpy.data.objects.remove(old,do_unlink=True)
front=camera('AQUA R3 | North Elevation Camera',(4,148,11),(0,39,4.8),50,84)
approach=camera('AQUA R3 | Street Approach Camera',(4,59,1.7),(70,-5,5),28)
inside=camera('AQUA R3 | Interior Gallery Camera',(48,-46,11),(13,0,3.8),35)
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1700; scene.render.resolution_y=1050; scene.render.resolution_percentage=80; scene.render.image_settings.file_format='PNG'; scene.camera=front
marker=bpy.data.objects.get('Morgan J. Burke Boilermaker Aquatic Center | official GIS footprint interior plinth')
if marker: marker['r3_revision']='Street View based north lettering scaled down and direct-mounted; north brick piers refined, real-scale procedural brick/roof material and roof seams added, mezzanine stairs/supports improved. Roof profile, seating/circulation dimensions remain schematic.'
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET)); print(json.dumps({'saved':str(ASSET),'sign_plaque_removed':True,'sign_text_size_m':letter.data.size,'thin_north_piers':sum(o.name.startswith('AQUA R3 | north brick pilaster') for o in asset.all_objects),'roof_seam_splines':len(curve.splines),'gallery_stairs_rebuilt':True,'gallery_supports':6,'master_shared_files_edited':False},indent=2))
