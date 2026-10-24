import bpy, math
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
asset=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
bpy.ops.wm.open_mainfile(filepath=str(asset))
# Use actual object-space X/Z coordinates so the front wall resolves as running-bond masonry at building scale.
mat=bpy.data.materials.new('AQUA R4 | north facade running-bond brick with readable mortar relief'); mat.diffuse_color=(0.39,0.12,0.075,1); mat.use_nodes=True
nt=mat.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); out.location=(720,40); bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); bs.location=(460,40); bs.inputs['Roughness'].default_value=.84
geo=nt.nodes.new('ShaderNodeNewGeometry'); geo.location=(-860,220); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); sep.location=(-650,220); comb=nt.nodes.new('ShaderNodeCombineXYZ'); comb.location=(-440,220); brick=nt.nodes.new('ShaderNodeTexBrick'); brick.location=(-200,220)
brick.inputs['Color1'].default_value=(.43,.16,.095,1); brick.inputs['Color2'].default_value=(.31,.09,.052,1); brick.inputs['Mortar'].default_value=(.19,.17,.15,1); brick.inputs['Scale'].default_value=1.0; brick.inputs['Brick Width'].default_value=.66; brick.inputs['Row Height'].default_value=.22; brick.inputs['Mortar Size'].default_value=.028; brick.inputs['Mortar Smooth'].default_value=.025
bump=nt.nodes.new('ShaderNodeBump'); bump.location=(210,-40); bump.inputs['Strength'].default_value=.42; bump.inputs['Distance'].default_value=.045
nt.links.new(geo.outputs['Position'],sep.inputs['Vector']); nt.links.new(sep.outputs['X'],comb.inputs['X']); nt.links.new(sep.outputs['Z'],comb.inputs['Y']); nt.links.new(brick.outputs['Color'],bs.inputs['Base Color']); nt.links.new(comb.outputs['Vector'],brick.inputs['Vector']); nt.links.new(brick.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']); nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
wall=bpy.data.objects['AQUA R1 | continuous brick and concrete high-bay envelope']; wall.data.materials.append(mat); mi=len(wall.data.materials)-1; assign=0
for poly in wall.data.polygons:
 c=poly.center
 if poly.normal.y>.9 and c.y>50.6 and c.z>.5:
  poly.material_index=mi; assign+=1
assert assign>0, 'No north-facing facade polygons assigned to mapped masonry'
# Make the sign readable but smaller than the previous overscale treatment; the source remains qualitative.
letter=bpy.data.objects['AQUA R1 | north facade building name']; letter.data.size*=.76; letter.data.align_x='CENTER'; letter.location.x=0.0
# Stronger, fine standing-seam relief across both estimated roof planes; dimensions/profile remain uncertain.
seams=bpy.data.objects['AQUA R3 | subtle standing seams on estimated roof']; seams.name='AQUA R4 | raised standing seams across estimated roof planes'; seams.data.bevel_depth=.043; seams.data.bevel_resolution=2
roofmat=bpy.data.materials.new('AQUA R4 | soft silver-gray raised roof seam metal'); roofmat.diffuse_color=(.31,.34,.36,1); roofmat.use_nodes=True; p=roofmat.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(.31,.34,.36,1); p.inputs['Metallic'].default_value=.42; p.inputs['Roughness'].default_value=.32
seams.data.materials.clear(); seams.data.materials.append(roofmat)
# Add soft frontal fill to reveal brick and relief in the north facade render.
ld=bpy.data.lights.new('AQUA R4 | soft north facade fill','AREA'); lo=bpy.data.objects.new('AQUA R4 | soft north facade fill',ld); bpy.context.scene.collection.objects.link(lo); lo.location=(0,107,27); lo.rotation_euler=(Vector((0,49,5))-lo.location).to_track_quat('-Z','Y').to_euler(); ld.energy=18000; ld.shape='DISK'; ld.size=48
# Cut a schematic central stair aisle through the east spectator bank and its precast tiers.
seats=bpy.data.objects['AQUA R2 | 300 individual schematic spectator seats']; mesh=seats.data; adj=[set() for _ in mesh.vertices]
for poly in mesh.polygons:
 vs=list(poly.vertices)
 for i,v in enumerate(vs): w=vs[(i+1)%len(vs)]; adj[v].add(w); adj[w].add(v)
seen=set(); comp_id={}; comps=[]
for i in range(len(adj)):
 if i in seen: continue
 stack=[i]; seen.add(i); ids=[]
 while stack:
  v=stack.pop(); ids.append(v)
  for w in adj[v]:
   if w not in seen: seen.add(w); stack.append(w)
 cy=sum(mesh.vertices[v].co.y for v in ids)/len(ids); ci=len(comps); comps.append((cy,ids))
 for v in ids: comp_id[v]=ci
remove={ci for ci,(cy,ids) in enumerate(comps) if abs(cy+.2)<.35}; faces=[]
for poly in mesh.polygons:
 if comp_id[poly.vertices[0]] not in remove: faces.append((list(poly.vertices),poly.material_index))
used=sorted({v for face,_ in faces for v in face}); remap={v:i for i,v in enumerate(used)}; new=bpy.data.meshes.new('AQUA R4 | schematic seating with center aisle gap'); new.from_pydata([mesh.vertices[v].co[:] for v in used],[],[[remap[v] for v in face] for face,_ in faces]); new.materials.clear()
for m in mesh.materials:new.materials.append(m)
for pnew,(_,mi0) in zip(new.polygons,faces): pnew.material_index=mi0
new.update(); old_mesh=seats.data; seats.data=new
# Break concrete rows at the center to form the aisle, restore the central stair treads at each tier.
oldsteps=[o for o in bpy.data.objects if o.name.startswith('AQUA R2 | east grandstand step ') and o.type=='MESH']
for o in oldsteps:
 x,y,z=o.location; dx,dy,dz=o.dimensions; material=o.data.materials[0] if o.data.materials else None
 for side in (-1,1):
  bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y+side*10.55,z)); piece=bpy.context.object; piece.name='AQUA R4 | split east grandstand step'; piece.dimensions=(dx,20.9,dz); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  if material:piece.data.materials.append(material)
  for c in list(piece.users_collection): c.objects.unlink(piece)
  bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center'].objects.link(piece)
 o.hide_render=True; o.hide_viewport=True
 # tread across the central 1.6m aisle, at the level of this stand tier.
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,0,z)); tread=bpy.context.object; tread.name='AQUA R4 | schematic center aisle tread'; tread.dimensions=(dx,1.6,dz); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if material:tread.data.materials.append(material)
 for c in list(tread.users_collection):c.objects.unlink(tread)
 bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center'].objects.link(tread)
for old_step in oldsteps: bpy.data.objects.remove(old_step, do_unlink=True)
if old_mesh.users==0: bpy.data.meshes.remove(old_mesh)
# Guardrails trace the stepped aisle edges; exact aisle geometry is schematic.
railmat=bpy.data.materials.get('AQUA | charcoal anodized metal')
for side in (-1,1):
 cu=bpy.data.curves.new('AQUA R4 | center aisle sloped handrail','CURVE'); cu.dimensions='3D'; cu.bevel_depth=.035; cu.bevel_resolution=3; sp=cu.splines.new('POLY'); sp.points.add(11)
 for i in range(12):
  x=15.88+i*.68; z=.62+i*.28+.24+1.02; sp.points[i].co=(x,side*.96,z,1)
 ob=bpy.data.objects.new('AQUA R4 | schematic center aisle handrail',cu); bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center'].objects.link(ob)
 if railmat:cu.materials.append(railmat)
# Dedicated close view makes seat rows, central aisle and gallery circulation legible.
camdata=bpy.data.cameras.new('AQUA R4 | spectator aisle detail camera'); cam=bpy.data.objects.new('AQUA R4 | spectator aisle detail camera',camdata); bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center'].objects.link(cam); cam.location=(38,-32,8); cam.rotation_euler=(Vector((20,2,3.1))-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.lens=48
bpy.ops.wm.save_as_mainfile(filepath=str(asset)); print('R4 saved: mapped facade faces',assign,'center aisle removed seat components',len(remove),'remaining seat faces',len(faces),'stair tiers',len(oldsteps),'roof seam depth',seams.data.bevel_depth)



