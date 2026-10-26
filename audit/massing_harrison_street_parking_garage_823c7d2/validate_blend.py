import bpy, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
blend=root/'modular/buildings/massing_harrison_street_parking_garage_823c7d2.blend'
# Running in Blender after --background --python this file is meant to inspect the current file opened by --blend.
coll=bpy.data.collections.get('Asset_massing_harrison_street_parking_garage_823c7d2')
objs=list(coll.objects) if coll else []
pts=[]
object_bounds=[]
for ob in objs:
    if ob.type=='MESH':
        vv=[ob.matrix_world @ v.co for v in ob.data.vertices]
        pts.extend(vv)
        if vv:
            object_bounds.append({'name':ob.name,'bounds_xyz_m':[[min(p[i] for p in vv),max(p[i] for p in vv)] for i in range(3)]})
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file: external.append(im.filepath)
names=[o.name for o in objs]
extremes={}
for axis,label in enumerate(('x','y','z')):
    extremes[label]={'min':min(object_bounds,key=lambda ob:ob['bounds_xyz_m'][axis][0]),'max':max(object_bounds,key=lambda ob:ob['bounds_xyz_m'][axis][1])}
result={'blend':str(blend.relative_to(root)),'exists':blend.exists(),'blender_version':bpy.app.version_string,'saved_render_engine':bpy.context.scene.render.engine,'scene_names':[s.name for s in bpy.data.scenes], 'collection_names':[c.name for c in bpy.data.collections],'target_collection_present':bool(coll),'object_count':len(objs),'mesh_object_count':sum(o.type=='MESH' for o in objs),'non_mesh_objects':[o.name for o in objs if o.type!='MESH'],'world_bounds_xyz_m':bounds,'overall_bounds_contributors':extremes,'structural_deck_bounds_xyz_m':next((ob['bounds_xyz_m'] for ob in object_bounds if ob['name']=='Parking deck 02 | structural slab'),None),'mesh_vertices':sum(len(o.data.vertices) for o in objs if o.type=='MESH'),'mesh_faces':sum(len(o.data.polygons) for o in objs if o.type=='MESH'),'materials':[m.name for m in bpy.data.materials],'unpacked_external_images':external,'linked_libraries':[lib.filepath for lib in bpy.data.libraries],'parking_decks':[o.name for o in objs if o.name.startswith('Parking deck')],'roof_deck_present':any('Roof deck' in n for n in names),'roof_parking_markings':[n for n in names if 'Roof parking stalls' in n],'roof_circulation_arrows':[n for n in names if 'Roof circulation arrows' in n],'central_roof_pavilion':[n for n in names if 'central open roof pavilion' in n],'estimated_pavilion_piers':[n for n in names if 'central roof pavilion pier' in n],'temp_preview_objects':[o.name for o in bpy.data.objects if o.name.startswith('TEMP_')]}
Path(root/'audit/massing_harrison_street_parking_garage_823c7d2/validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
