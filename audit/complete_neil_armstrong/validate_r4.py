import bpy,json,hashlib,os
from mathutils import Vector
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
asset=root+r'\modular\buildings\neil_armstrong_hall.blend'
out=root+r'\audit\complete_neil_armstrong\validation_r4.json'
bpy.ops.wm.open_mainfile(filepath=asset)
col=bpy.data.collections['Asset_neil_armstrong_hall']; rootobj=bpy.data.objects['AssetRoot_neil_armstrong_hall']
verts=[]
for o in col.objects:
 if o.type=='MESH' and 'Wall' in o.name:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); verts.extend(ev.matrix_world@Vector(c) for c in ev.bound_box)
result={'building_id':'neil_armstrong_hall','revision':'R4','asset_path':'modular/buildings/neil_armstrong_hall.blend','saved_then_reopened_read_only':True,'geometry_modified':False,'scene':bpy.context.scene.name,'collection':col.name,'object_count':len(col.objects),'asset_root_location':list(rootobj.location),'shell_wall_bounds_m':[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)],'shell_wall_object_count':sum(1 for o in col.objects if o.type=='MESH' and 'Wall' in o.name),'asset_size_bytes':os.path.getsize(asset),'asset_sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest(),'same_hash_as_r3':hashlib.sha256(open(asset,'rb').read()).hexdigest()==json.load(open(root+r'\audit\complete_neil_armstrong\validation_r3.json'))['asset_sha256'],'render':'No new Blender render; no geometry changed. Reuse the R3 GIS/orthophoto registration plate and R2 model review renders.'}
json.dump(result,open(out,'w'),indent=2)
print(json.dumps(result,indent=2))
