import bpy,json,os
from mathutils import Vector
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_potter_engineering']
def bb(o):
 p=[o.matrix_world@v.co for v in o.data.vertices]
 return [[round(min(v[i] for v in p),4) for i in range(3)],[round(max(v[i] for v in p),4) for i in range(3)]]
keys=['AssetRoot_potter_engineering','POTR_Official_864_Structural_Envelope','POTR_Official_864_Roof','POTR_Historic2016_Room401_Penthouse_Massing']
res={'filepath':bpy.data.filepath,'object_count':len(c.all_objects),'objects':{},'stairs':[],'slabs':[],'render':{}}
for n in keys:
 o=c.objects.get(n);res['objects'][n]={'location':list(o.location),'dimensions':list(o.dimensions),'bounds':bb(o) if o.type=='MESH' else None,'parent':o.parent.name if o.parent else None,'materials':[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []}
for o in c.all_objects:
 if '_Level' in o.name and o.name.endswith('_Flight') or 'Basement_Landing' in o.name or o.name.endswith('_UpperLanding'):
  res['stairs'].append({'name':o.name,'bounds':bb(o) if o.type=='MESH' else None,'verts':len(o.data.vertices),'faces':len(o.data.polygons)})
 if 'Slab_Level' in o.name or '4S04' in o.name:
  res['slabs'].append({'name':o.name,'bounds':bb(o) if o.type=='MESH' else None,'verts':len(o.data.vertices),'faces':len(o.data.polygons)})
print(json.dumps(res,indent=2))
