import bpy,json,hashlib
from pathlib import Path
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
o=bpy.data.objects['ARMS_Cantilever_Canopy_Deck']
rows=[]
for i,m in enumerate(o.data.materials):
 b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m and m.use_nodes else None
 rows.append({'i':i,'name':m.name if m else None,'diffuse':list(m.diffuse_color) if m else None,'base':list(b.inputs['Base Color'].default_value) if b else None,'metal':float(b.inputs['Metallic'].default_value) if b else None,'rough':float(b.inputs['Roughness'].default_value) if b else None})
counts={i:sum(1 for f in o.data.polygons if f.material_index==i) for i in range(len(o.data.materials))}
areas={i:round(sum(f.area for f in o.data.polygons if f.material_index==i),2) for i in range(len(o.data.materials))}
images=[{'name':im.name,'filepath':im.filepath,'packed':im.packed_file is not None} for im in bpy.data.images if im.source=='FILE']
print(json.dumps({'objects':len(bpy.data.objects),'collection':len(bpy.data.collections['Asset_neil_armstrong_hall'].objects),'verts':len(o.data.vertices),'faces':len(o.data.polygons),'mats':rows,'counts':counts,'areas':areas,'images':images},indent=2))
