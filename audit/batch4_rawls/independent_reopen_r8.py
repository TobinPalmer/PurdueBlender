import bpy, os, json, hashlib
from mathutils import Vector
path = os.path.abspath('modular/buildings/rawls_hall.blend')
with open(path,'rb') as f: sha = hashlib.sha256(f.read()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=path)
scene=bpy.context.scene
bpy.context.view_layer.update()
def mat4(m): return [[round(float(m[r][c]),9) for c in range(4)] for r in range(4)]
def bounds(obj):
    pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [[round(min(p[i] for p in pts),6),round(max(p[i] for p in pts),6)] for i in range(3)]
root=bpy.data.objects.get('AssetRoot_rawls_hall'); shell=bpy.data.objects.get('RAWL_Masonry_Exterior_Walls')
fixed=['Cam_RAWL_01_North_StateSt','Cam_RAWL_02_NW_Curved_Rotunda','Cam_RAWL_03_West_GrantSt_Skywalk','Cam_RAWL_04_SE_Diagonal_Facade','Cam_RAWL_05_Roof_Arched_Penthouse','Cam_RAWL_06_Ortho_Footprint_Top','RAWL_Site_Sidewalk_Apron','RAWL_South_Windows_South_BronzeMullions']
objrows=[]
for name in fixed:
    o=bpy.data.objects.get(name)
    objrows.append({'name':name,'found':bool(o),'type':o.type if o else None,'parent':o.parent.name if o and o.parent else None,'location':list(o.location) if o else None,'parent_inverse':mat4(o.matrix_parent_inverse) if o else None,'world_bounds':bounds(o) if o else None})
meshrows=[]
for o in scene.objects:
    if o.type=='MESH':
        b=bounds(o)
        if any(abs(v)>120 for axis in b[:2] for v in axis): meshrows.append({'name':o.name,'world_bounds':b})
result={'asset':path,'sha256':sha,'scene':scene.name,'scene_objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'collections':[{'name':c.name,'scene_objects':sum(o.name in scene.objects for o in c.objects)} for c in bpy.data.collections if any(o.name in scene.objects for o in c.objects)],'root':{'found':bool(root),'world_matrix':mat4(root.matrix_world) if root else None},'shell':{'found':bool(shell),'world_matrix':mat4(shell.matrix_world) if shell else None,'world_bounds':bounds(shell) if shell else None},'materialless_meshes':[o.name for o in scene.objects if o.type=='MESH' and len(o.data.materials)==0],'external_images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE'],'linked_libraries':[l.filepath for l in bpy.data.libraries if l.filepath],'fixed_objects':objrows,'world_bound_outliers_over_120m':meshrows}
print(json.dumps(result,indent=2))
with open('audit/batch4_rawls/independent_reopen_r8.json','w',encoding='utf-8') as f: json.dump(result,f,indent=2)

