import bpy, json, hashlib, sys
from pathlib import Path
blend=Path(bpy.data.filepath)
coll=bpy.data.collections.get('Asset_winifred_parker_hall')
if coll is None: raise RuntimeError('Export collection missing')
obj=bpy.data.objects.get('Parker_EastWing_MainMass')
if obj is None: raise RuntimeError('Expected duplicate EastWing mass missing')
if obj.name not in coll.objects: raise RuntimeError('Duplicate object is not a direct export member')
old={'name':obj.name,'data':obj.data.name,'verts':len(obj.data.vertices),'faces':len(obj.data.polygons),'location':list(obj.location),'dimensions':list(obj.dimensions),'material':obj.data.materials[0].name if obj.data.materials else None,'parent':obj.parent.name if obj.parent else None}
bpy.data.objects.remove(obj,do_unlink=True)
out=blend.parent/'Winifred_Parker_R4_candidate.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'candidate':str(out),'source_sha256':hashlib.sha256(Path('modular/buildings/winifred_parker_hall.blend').read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'removed_object':old,'remaining_export_objects':len(coll.all_objects),'remaining_export_meshes':sum(o.type=='MESH' for o in coll.all_objects),'change_reason':'The old full-height EastWing box completely obscures the pass-2 split masses intended to expose the documented suite cutaway. It is removed only in this candidate for visual and structural review.'}
Path('audit/winifred_parker_hall/east_wing_duplicate_candidate_change.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))