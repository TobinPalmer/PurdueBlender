import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
c=bpy.data.collections['Asset_stewart_center']; root=bpy.data.objects['AssetRoot_stewart_center']
def bounds(objs):
 pts=[o.matrix_world@Vector(v) for o in objs if o.type in {'MESH','CURVE','FONT'} for v in o.bound_box]
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
walls=[o for o in c.all_objects if o.name.startswith('STEW_Ext_Wall_GIS_')]
interiors={}
for name,pred in {'Loeb theater':lambda n:n.startswith('Loeb_'),'HSSE library':lambda n:n.startswith('HSSE_'),'Ringel Gallery':lambda n:n.startswith('Ringel_')}.items():
 objs=[o for o in c.all_objects if pred(o.name)]
 interiors[name]={'object_count':len(objs),'local_bounds_m':bounds(objs)}
report={'asset':str(Path(bpy.data.filepath).resolve()),'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'collection':c.name,'root':{'name':root.name,'location':list(root.location),'world_matrix':[[float(v) for v in row] for row in root.matrix_world]},'collection_object_count':len(list(c.all_objects)),'structural_wall_count':len(walls),'structural_wall_local_bounds_m':bounds(walls),'GIS_trace_vertices':int(bpy.context.scene.get('stewart_gis_footprint_vertices',0)),'GIS_area_m2':float(bpy.context.scene.get('stewart_gis_area_m2',0)),'wall_height_m':'16.5 (estimated; no elevation source)','roof':'Flat polygon following traced GIS shell; elevation and rooftop forms estimated','interior_module_bounds':interiors}
(HERE/'building_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
