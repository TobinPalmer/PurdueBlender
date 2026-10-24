import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
rows=[]
for name in ['AQUA R3 | subtle standing seams on estimated roof','AQUA R1 | north facade building name','AQUA R1 | continuous brick and concrete high-bay envelope']:
 o=bpy.data.objects[name]; rows.append({'name':name,'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'dims':list(o.dimensions),'scale':list(o.scale),'mat':[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []})
 if o.type=='CURVE':rows[-1]['bevel_depth']=o.data.bevel_depth;rows[-1]['bevel_resolution']=o.data.bevel_resolution;rows[-1]['resolution_u']=o.data.resolution_u
mats=[]
for m in bpy.data.materials:
 if any(s in m.name.lower() for s in ['brick','roof','masonry']):
  d={'name':m.name,'nodes':[]}
  if m.node_tree:
   for n in m.node_tree.nodes:
    d['nodes'].append({'type':n.bl_idname,'name':n.name,'inputs':{inp.name:inp.default_value[:] if hasattr(inp.default_value,'__len__') else inp.default_value for inp in n.inputs if hasattr(inp,'default_value')}})
  mats.append(d)
Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_boilermaker_aquatic_r1\inspect_r3_materials.json').write_text(json.dumps({'objects':rows,'materials':mats},indent=2))
