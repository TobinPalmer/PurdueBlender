import bpy, math, json
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
# Tuck floor slab perimeters just behind the outer masonry face to prevent coplanar z-fighting/exposed bands.
slabs=[o for o in bpy.data.objects if o.name.startswith('KRCH | schematic level slab')]
for o in slabs:
 for v in o.data.vertices:
  x,y=v.co.x,v.co.y; r=math.hypot(x,y)
  if r>1e-6:
   inset=0.28; scale=max(0.0,(r-inset)/r); v.co.x*=scale; v.co.y*=scale
 o.data.update(); o['perimeter_setback_m']=0.28
stair=bpy.data.objects['KRCH | four-story visible switchback stair and etched glass guard']
for m in stair.data.materials:
 if m and 'visible lobby cast stone stair treads' in m.name:
  m.diffuse_color=(0.86,0.81,0.68,1); m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:
   bs.inputs['Base Color'].default_value=(0.86,0.81,0.68,1); bs.inputs['Roughness'].default_value=0.62
   if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value=(0.18,0.14,0.08,1); bs.inputs['Emission Strength'].default_value=0.18
# Clearer glass helps the source-supported public stair read through the lobby wall.
for name in ['KRCH | clear blue-gray lobby glazing','KRCH | translucent etched glass gallery guards']:
 m=bpy.data.materials.get(name)
 if m:
  a=0.09 if 'lobby glazing' in name else 0.32
  m.diffuse_color=(0.54,0.69,0.70,a); m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:
   bs.inputs['Base Color'].default_value=(0.54,0.69,0.70,a); bs.inputs['Alpha'].default_value=a; bs.inputs['Roughness'].default_value=0.13
   if 'Transmission Weight' in bs.inputs: bs.inputs['Transmission Weight'].default_value=0.16
  m.surface_render_method='DITHERED'
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'slabs':len(slabs),'perimeter_inset_m':0.28,'stair_material':'high-contrast warm cast stone','glazing_alpha':0.09},indent=2))
