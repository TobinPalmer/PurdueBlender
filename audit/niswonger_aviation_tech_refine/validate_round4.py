"""Fresh Blender reopen validation and local inventory for Niswonger R4."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); OUT=ROOT/'audit/niswonger_aviation_tech_refine'; blend=Path(bpy.data.filepath)
a=bpy.data.collections.get('Asset_niswonger_aviation_tech');assert a
objs=sorted(a.all_objects,key=lambda o:o.name); names=[o.name for o in objs]
mesh=[o for o in objs if o.type=='MESH'];root=bpy.data.objects.get('AssetRoot_niswonger_aviation_tech');assert root
unmat=[o.name for o in mesh if not o.data.materials]
missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
roofs=['NISW_R2_Roof_Brick_Wing','NISW_R2_Roof_Classroom_Wing','NISW_Photographic_Sloping_Roof','NISW_Flat_Roof_Membrane']
assert all(not bpy.data.objects[n].hide_render for n in roofs)
cluster=bpy.data.objects.get('NISW_R4_Roof_HVAC_Cluster');assert cluster and cluster in objs
assert not unmat and not missing
assert root.location.length<1e-8
assert cluster.get('extent_status') and cluster.get('detail_status')
cs=[cluster.matrix_world@Vector(v) for v in cluster.bound_box]
cluster_bounds=[[round(min(v[i] for v in cs),4) for i in range(3)],[round(max(v[i] for v in cs),4) for i in range(3)]]
# Ensure cluster footprint remains inside the approximate classroom roof field.
assert cluster_bounds[0][0] > -31.7 and cluster_bounds[1][0] < 4.84, cluster_bounds
assert cluster_bounds[0][1] > 7.15 and cluster_bounds[1][1] < 43.95, cluster_bounds
sha=hashlib.sha256(blend.read_bytes()).hexdigest()
summary={'revision':'R4','fresh_reopen':True,'asset_path':str(blend),'sha256':sha,'collection':a.name,'object_count':len(objs),'mesh_count':len(mesh),'root_location':[round(x,6) for x in root.location],'new_object':'NISW_R4_Roof_HVAC_Cluster','cluster_bounds_local':cluster_bounds,'cluster_materials':[m.name if m else None for m in cluster.data.materials],'cluster_source_basis':cluster.get('source_basis'),'cluster_extent_status':cluster.get('extent_status'),'render_visible_roof_shells':{n: not bpy.data.objects[n].hide_render for n in roofs},'unmaterialed_meshes':unmat,'missing_external_images':missing,'object_names':names}
(OUT/'reopen_validation_r4.json').write_text(json.dumps(summary,indent=2))
(OUT/'asset_inventory_r4.json').write_text(json.dumps({'asset_id':'niswonger_aviation_tech','collection':a.name,'asset_path':'modular/buildings/niswonger_aviation_tech.blend','revision':'R4','sha256':sha,'object_count':len(objs),'mesh_count':len(mesh),'object_names':names,'source_evidence':['audit/niswonger_aviation_tech_refine/roof_source_evidence_r3.md','audit/niswonger_aviation_tech_refine/roof_equipment_evidence_r4.md','audit/niswonger_aviation_tech_refine/registered_roof_overlay_r3.png']},indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='object_names'},indent=2))
