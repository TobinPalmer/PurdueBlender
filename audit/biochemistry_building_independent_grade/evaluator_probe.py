import bpy, json, math, os, sys
from mathutils import Vector

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
grade = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join(root, 'modular', 'buildings', 'biochemistry_building.blend')
manifest_path = os.path.join(root, 'modular', 'manifest.json')
gis_path = os.path.join(grade, 'sources', 'biochemistry_building_gis_fid238_2026-10-25.json')
mode = sys.argv[-1]
with open(manifest_path, encoding='utf-8') as f: manifest=json.load(f)
entry=next(a for a in manifest['assets'] if a['id']=='biochemistry_building')
with open(gis_path, encoding='utf-8') as f: feature=json.load(f)['features'][0]
attrs=feature['attributes']
lon0,lat0=-86.9137,40.4274
sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
ll=feature['geometry']['rings'][0][:-1]
ringxy=[((p[0]-lon0)*sx,(p[1]-lat0)*sy) for p in ll]
cross=[ringxy[i][0]*ringxy[(i+1)%len(ringxy)][1]-ringxy[(i+1)%len(ringxy)][0]*ringxy[i][1] for i in range(len(ringxy))]
a2=sum(cross); cx=sum((ringxy[i][0]+ringxy[(i+1)%len(ringxy)][0])*cross[i] for i in range(len(ringxy)))/(3*a2); cy=sum((ringxy[i][1]+ringxy[(i+1)%len(ringxy)][1])*cross[i] for i in range(len(ringxy)))/(3*a2)
local=[(x-cx,y-cy) for x,y in ringxy]

def bounds_objects(objects):
    pts=[]
    for o in objects:
        if o.type=='MESH': pts.extend(o.matrix_world @ Vector(c) for c in o.bound_box)
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]

if mode=='asset':
    col=bpy.data.collections.get(entry['collection'])
    assert bpy.context.scene.name==entry['scene'] and col
    names=sorted(o.name for o in col.objects); expected=sorted(entry['objects'])
    shell=bpy.data.objects.get('biochemistry_building_GIS_outline_primary_shell')
    vertices=[((shell.matrix_world @ v.co).x,(shell.matrix_world @ v.co).y) for v in shell.data.vertices[:len(local)]]
    verr=[min(math.dist(p,q) for q in vertices) for p in local]
    mesh=[o for o in col.objects if o.type=='MESH']; mats=sorted({m.name for o in mesh for m in o.data.materials if m})
    image_paths=[i.filepath for i in bpy.data.images if i.source!='GENERATED' and i.filepath]
    linked_libs=[l.filepath for l in bpy.data.libraries if l.filepath]
    result={'mode':'asset','scene':bpy.context.scene.name,'collection':col.name,'object_count':len(col.objects),'manifest_count':len(expected),'exact_manifest_names_match':names==expected,'missing_names':sorted(set(expected)-set(names))[:20],'unexpected_names':sorted(set(names)-set(expected))[:20],'type_counts':{t:sum(o.type==t for o in col.objects) for t in sorted({o.type for o in col.objects})},'parented_object_count':sum(o.parent is not None for o in col.objects),'shell':shell.name,'shell_vertex_count':len(shell.data.vertices),'gis_unique_vertices':len(local),'max_gis_shell_vertex_nearest_error_m':max(verr),'gis_centroid_xy_m':[cx,cy],'manifest_origin_xy_m':entry['placement_origin_xy_m'],'gis_to_manifest_origin_error_m':math.dist((cx,cy),entry['placement_origin_xy_m']),'bounds_m':bounds_objects(col.objects),'material_count':len(mats),'material_names':mats,'external_image_paths':image_paths,'linked_library_paths':linked_libs,'gis_attributes':attrs,'gis_unique_ring_vertices':len(local)}
    out=os.path.join(grade,'asset_probe.json'); json.dump(result,open(out,'w',encoding='utf-8'),indent=2)
    # Write an independent collection-only linked library, then validate in a distinct invocation.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(asset_path,link=True) as (src,dst):
        assert entry['collection'] in src.collections
        dst.collections=[entry['collection']]
    linked=next(c for c in dst.collections if c)
    bpy.context.scene.collection.children.link(linked)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(grade,'independent_collection_link.blend'))
    print(json.dumps(result,indent=2))
elif mode=='master':
    marker=bpy.data.objects.get('Placement_biochemistry_building')
    result={'mode':'master','scene':bpy.context.scene.name,'marker_found':bool(marker)}
    if marker:
        result.update({'marker_location':list(marker.location),'marker_rotation_euler':list(marker.rotation_euler),'marker_scale':list(marker.scale),'marker_type':marker.type,'marker_instance_collection':marker.instance_collection.name if marker.instance_collection else None,'marker_collection_paths':[c.name for c in marker.users_collection]})
    out=os.path.join(grade,'master_placement_probe.json'); json.dump(result,open(out,'w',encoding='utf-8'),indent=2)
    print(json.dumps(result,indent=2))
elif mode=='reopen':
    col=bpy.data.collections.get(entry['collection']); names=sorted(o.name for o in col.objects) if col else []
    result={'mode':'independent_export_reopen','collection_found':bool(col),'reopened_object_count':len(names),'manifest_count':len(entry['objects']),'exact_manifest_names_match':names==sorted(entry['objects']),'camera_or_light_count':sum(o.type in {'CAMERA','LIGHT'} for o in col.objects) if col else None,'linked_library_paths':[l.filepath for l in bpy.data.libraries if l.filepath]}
    json.dump(result,open(os.path.join(grade,'export_reopen_probe.json'),'w',encoding='utf-8'),indent=2); print(json.dumps(result,indent=2))
