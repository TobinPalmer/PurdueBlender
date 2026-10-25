import bpy, json, hashlib, struct, os
from pathlib import Path

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
BACKUP=ROOT/'modular/buildings/neil_armstrong_hall.blend1'
MASTER=ROOT/'purdue_campus_master.blend'
MANIFEST=ROOT/'modular/manifest.json'
OUT=ROOT/'audit/neil_armstrong_hall_refine/independent_reopen_validation_r12.json'
EXPECTED='d3d90d21ad60b985826270be18c016220944e3c87545fc179af7b51d5084b8b4'


def digest_scene():
    col=bpy.data.collections.get('Asset_neil_armstrong_hall')
    if not col: raise RuntimeError('asset collection missing')
    h=hashlib.sha256()
    objs=sorted(col.objects,key=lambda x:x.name)
    for o in objs:
        h.update(o.name.encode('utf-8')+b'\0'+o.type.encode('ascii')+b'\0')
        for x in o.matrix_world:
            for y in x: h.update(struct.pack('<d',float(y)))
        if o.type=='MESH' and o.data:
            for v in o.data.vertices:
                for c in v.co: h.update(struct.pack('<d',float(c)))
            h.update(b'|POLYGONS|')
            for p in o.data.polygons:
                h.update(struct.pack('<I',len(p.vertices)))
                for i in p.vertices: h.update(struct.pack('<I',i))
    return h.hexdigest(),objs

def read_asset(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    col=bpy.data.collections.get('Asset_neil_armstrong_hall')
    root=bpy.data.objects.get('AssetRoot_neil_armstrong_hall')
    digest,objs=digest_scene()
    mesh=[o for o in objs if o.type=='MESH']
    missing_materials=[o.name for o in mesh if not o.data.materials or any(m is None for m in o.data.materials)]
    image_records=[]
    for im in bpy.data.images:
        if im.source!='FILE': continue
        resolved=bpy.path.abspath(im.filepath)
        image_records.append({'name':im.name,'filepath':im.filepath,'resolved':resolved,'packed':bool(im.packed_file),'exists':bool(im.packed_file or os.path.exists(resolved))})
    coarse={}
    for name in ['ARMS_R5_Coarse_LiDAR_wing_low','ARMS_R5_Coarse_LiDAR_wing_mid','ARMS_R5_Coarse_LiDAR_roof_high']:
        o=bpy.data.objects.get(name)
        coarse[name]={'exists':o is not None,'hide_render':o.hide_render if o else None,'hide_viewport':o.hide_viewport if o else None,'hide_get':o.hide_get() if o else None,'in_asset_collection':bool(o and col and o.name in col.objects)}
    canopy={}
    for name in ['ARMS_Cantilever_Canopy_Deck','ARMS_Canopy_Fascia_Trim']:
        o=bpy.data.objects.get(name)
        canopy[name]={'exists':o is not None,'materials':[m.name for m in o.data.materials if m] if o and o.type=='MESH' else [],'material_slots':[s.material.name if s.material else None for s in o.material_slots] if o else []}
    mat=bpy.data.materials.get('ARMS_Sea_Wolf_ACM')
    mat_info=None
    if mat and mat.use_nodes:
        bsdf=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        output=next((n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL'),None)
        linked=bool(bsdf and output and any(l.from_node==bsdf and l.to_node==output for l in mat.node_tree.links))
        mat_info={'exists':True,'node_based':True,'principled_output_linked':linked,'base_color':list(bsdf.inputs['Base Color'].default_value) if bsdf else None,'metallic':float(bsdf.inputs['Metallic'].default_value) if bsdf else None,'roughness':float(bsdf.inputs['Roughness'].default_value) if bsdf else None}
    else: mat_info={'exists':bool(mat),'node_based':bool(mat and mat.use_nodes)}
    return {'file':str(path),'scene':bpy.context.scene.name,'collection_object_count':len(objs),'scene_object_count':len(bpy.data.objects),'mesh_count':len(mesh),'material_count':len(bpy.data.materials),'geometry_world_transform_sha256':digest,'root_location':list(root.location) if root else None,'root_matrix_world':[[float(x) for x in row] for row in root.matrix_world] if root else None,'coarse_envelopes':coarse,'canopy_objects':canopy,'sea_wolf_material':mat_info,'meshes_without_valid_material':missing_materials,'external_file_images':image_records,'external_missing_images':[x for x in image_records if not x['exists']]},set(o.name for o in objs)

asset_report,asset_names=read_asset(ASSET)
backup_report,backup_names=read_asset(BACKUP)
manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
entry=next(x for x in manifest['assets'] if x['id']=='neil_armstrong_hall')
expected_names=set(entry['objects'])
master_marker=None
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
marker=bpy.data.objects.get('Placement_neil_armstrong_hall')
if marker:
    inst=marker.instance_collection
    master_marker={'exists':True,'location':[float(v) for v in marker.location],'rotation_euler':[float(v) for v in marker.rotation_euler],'scale':[float(v) for v in marker.scale],'instance_type':marker.instance_type,'instance_collection':inst.name if inst else None,'instance_library_filepath':bpy.path.abspath(inst.library.filepath) if inst and inst.library else None}
else:
    master_marker={'exists':False}
origin=entry.get('placement_origin_xy_m')
error=None
if marker and origin:
    error=[float(marker.location.x-origin[0]),float(marker.location.y-origin[1]),float(marker.location.z)]
master_marker['manifest_origin_xy_m']=origin
master_marker['marker_minus_manifest_xyz_m']=error
master_neil_libs=[bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries if 'neil_armstrong_hall.blend' in lib.filepath.lower()]
master_marker['library_datablocks_referencing_asset']=master_neil_libs

actual_hash=hashlib.sha256(ASSET.read_bytes()).hexdigest()
res={'task':'independent read-only R11 verification','asset_sha256':actual_hash,'provided_sha256_matches':actual_hash.lower()==EXPECTED,'asset':asset_report,'previous_blend1_snapshot':backup_report,'geometry_hash_matches_prior_snapshot':asset_report['geometry_world_transform_sha256']==backup_report['geometry_world_transform_sha256'],'object_names_match_prior_snapshot':asset_names==backup_names,'manifest':{'building_id':entry['id'],'kind':entry['kind'],'asset_file':entry['file'],'collection':entry['collection'],'scene':entry['scene'],'object_count_field':entry['object_count'],'listed_object_names_count':len(expected_names),'asset_object_count':asset_report['collection_object_count'],'listed_names_match_asset':expected_names==asset_names,'missing_names':sorted(expected_names-asset_names),'unlisted_names':sorted(asset_names-expected_names),'placement_origin_xy_m':origin,'accuracy_status':entry.get('accuracy_status')},'master_placement':master_marker,'blender_version':bpy.app.version_string}
OUT.write_text(json.dumps(res,indent=2),encoding='utf-8')
print(json.dumps(res,indent=2))
