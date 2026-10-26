import bpy, json, os, hashlib, math
from collections import Counter
from mathutils import Vector
id='massing_university_street_parking_garage_pgu_be81bec'
asset_coll=bpy.data.collections.get('Asset_'+id)
assert bpy.context.scene.name=='Building_'+id and asset_coll
asset_path=bpy.data.filepath
objects=[]
allverts=[]
materials=Counter(); object_types=Counter(); names=Counter()
for o in asset_coll.objects:
    object_types[o.type]+=1; names[o.name.split(' | ')[0].split(' E')[0].split(' L')[0]]+=1
    mats=[m.name for m in getattr(o.data,'materials',[]) if m]
    for m in mats: materials[m]+=1
    if o.type=='MESH':
        ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
        bounds=[]
        for v in me.vertices:
            p=o.matrix_world @ v.co; allverts.append(p); bounds.append(p)
        if bounds:
            mi=[min(v[i] for v in bounds) for i in range(3)]; ma=[max(v[i] for v in bounds) for i in range(3)]
        else: mi=ma=[0,0,0]
        objects.append({'name':o.name,'bounds':[mi,ma],'dimensions':[ma[i]-mi[i] for i in range(3)],'verts':len(me.vertices),'polys':len(me.polygons),'materials':mats})
        ev.to_mesh_clear()
    elif o.type=='FONT': objects.append({'name':o.name,'type':'FONT','body':o.data.body})
mn=[min(v[i] for v in allverts) for i in range(3)]; mx=[max(v[i] for v in allverts) for i in range(3)]
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file: external.append(im.filepath)
result={'blend':asset_path,'scene':bpy.context.scene.name,'asset_collection':asset_coll.name,'placement_origin_xy_m':list(asset_coll.get('placement_origin_xy_m',[])),'total_scene_objects':len(bpy.context.scene.objects),'asset_objects':len(asset_coll.objects),'asset_object_types':dict(object_types),'evaluated_asset_bounds':{'min':mn,'max':mx,'dimensions':[mx[i]-mn[i] for i in range(3)]},'materials':dict(materials),'external_unpacked_images':external,'object_name_groups':dict(names),'objects':objects}
out=os.path.join(os.path.dirname(asset_path),'..','..','audit','university_street_garage_pgu','independent_grade_final','fresh_blender_probe.json')
with open(out,'w') as f: json.dump(result,f,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='objects'},indent=2))
