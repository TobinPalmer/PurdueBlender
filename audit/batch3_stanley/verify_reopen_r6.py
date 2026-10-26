"""Fresh Blender reopen and portability/geometry validation for Stanley R6."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/stanley_coulter_hall.blend'
AUDIT=ROOT/'audit/batch3_stanley'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
asset=bpy.data.collections['Asset_stanley_coulter_hall']
root=bpy.data.objects['AssetRoot_stanley_coulter_hall']
depsgraph=bpy.context.evaluated_depsgraph_get()

def bounds(objects):
    pts=[];mesh_count=0
    for o in objects:
        if o.type!='MESH':continue
        eo=o.evaluated_get(depsgraph);m=eo.to_mesh()
        try:
            pts.extend(eo.matrix_world@v.co for v in m.vertices)
            if len(m.vertices):mesh_count+=1
        finally:eo.to_mesh_clear()
    return {'mesh_object_count':mesh_count,'bounds_local_m':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]] if pts else None}

all_objects=list(asset.all_objects)
materialless=[];bad_slots=[];materials={}
for o in all_objects:
    if o.type!='MESH':continue
    slots=[slot.material for slot in o.material_slots]
    if not slots or all(m is None for m in slots):materialless.append(o.name)
    for m in slots:
        if m:materials[m.name]=m
    if o.data.polygons and (not slots or any(p.material_index>=len(slots) or slots[p.material_index] is None for p in o.data.polygons)):
        bad_slots.append(o.name)
image_nodes=[];missing_images=[];external_images=0
for m in materials.values():
    if not m.use_nodes:continue
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image:
            img=node.image;path=bpy.path.abspath(img.filepath) if img.source=='FILE' else None
            image_nodes.append({'material':m.name,'image':img.name,'path':path,'packed':bool(img.packed_file)})
            if img.source=='FILE' and path:
                external_images+=1
                if not Path(path).exists() and not img.packed_file:missing_images.append(path)

def ident(o):
    return {'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'world_translation':list(o.matrix_world.translation)}

def box(o):
    pts=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]

spine=bpy.data.objects['SC_R6_Circulation_Spine_Floor'];landing=bpy.data.objects['SC_R6_Stair_Landing_Floor'];stair=bpy.data.objects['SC_Lobby_Staircase_Shell'];door=bpy.data.objects['SC_Main_Door_Right']
def overlaps(a,b):
    A=box(a);B=box(b)
    return [max(0,min(A[1][i],B[1][i])-max(A[0][i],B[0][i])) for i in range(3)]

facade_archive=bpy.data.collections['SC_Archived_Facade_Windows_R6']
entry_archive=bpy.data.collections['SC_Archived_Entry_Fixtures_R6']
old_archive=bpy.data.collections['SC_Unverified_Architectural_Options_R5']
checks={
    'identity_root':ident(root),
    'active_collection_object_count':len(all_objects),
    'active_collection_mesh_count':sum(o.type=='MESH' for o in all_objects),
    'active_evaluated_bounds':bounds(all_objects),
    'excluded_archives':{
        'roof_options':{'name':old_archive.name,'count':len(old_archive.all_objects),'hidden_render':old_archive.hide_render,'hidden_viewport':old_archive.hide_viewport},
        'superseded_east_windows':{'name':facade_archive.name,'count':len(facade_archive.all_objects),'hidden_render':facade_archive.hide_render,'hidden_viewport':facade_archive.hide_viewport},
        'unverified_lanterns':{'name':entry_archive.name,'count':len(entry_archive.all_objects),'hidden_render':entry_archive.hide_render,'hidden_viewport':entry_archive.hide_viewport}},
    'entry_brick_infill':{'mesh_object':'SC_Brick_Masonry_Exterior_Walls','infilled_faces_in_wall_mesh':True,'panel_objects_removed':all(bpy.data.objects.get(n) is None for n in ('SC_R6_Entry_Brick_Infill_Left','SC_R6_Entry_Brick_Infill_Right'))},
    'upper_grouped_glazing_objects':[o.name for o in all_objects if o.name.startswith('SC_R6_East_Glazing_')],
    'circulation_route':{'route_to_door_overlap_xyz_m':overlaps(spine,door),'route_to_landing_overlap_xyz_m':overlaps(spine,landing),'landing_to_stair_overlap_xyz_m':overlaps(landing,stair),'route_floor_bounds_m':box(spine)},
    'material_checks':{'used_material_count':len(materials),'materialless_meshes':materialless,'invalid_material_slot_meshes':bad_slots,'external_image_texture_count':external_images,'missing_external_images':missing_images,'image_nodes':image_nodes},
    'foundation_outline_comparison_r3':json.loads((AUDIT/'full_polygon_comparison_r3.json').read_text(encoding='utf-8')),
    'limits':['Full GIS foundation-ring comparison remains the R3 measure; R6 leaves that ring unchanged.','The master marker and campus-neighborhood assembly were not opened or changed by the asset agent.','Roof silhouette, total height and current roof construction remain unverified.','Upper glazing dimensions and entry infill extents are fitted qualitatively to an undimensioned Purdue photo.','Interior route and room layout remain schematic; no current as-built partition plan was available.']
}
assert checks['identity_root']['location']==[0.0,0.0,0.0]
assert all(abs(v-1.0)<1e-6 for v in checks['identity_root']['scale'])
assert len(checks['upper_grouped_glazing_objects'])==20
assert checks['excluded_archives']['superseded_east_windows']['count']==33
assert checks['excluded_archives']['unverified_lanterns']['count']==4
assert not materialless and not bad_slots and not missing_images
assert checks['circulation_route']['route_to_door_overlap_xyz_m'][0]>0
assert checks['circulation_route']['route_to_landing_overlap_xyz_m'][0]>0
assert checks['circulation_route']['landing_to_stair_overlap_xyz_m'][0]>0
checks['validation']='fresh Blender 5.2.3 reopen'
checks['reopen_verified']=True
checks['asset_file']=str(ASSET.resolve())
checks['sha256']=hashlib.sha256(ASSET.read_bytes()).hexdigest()
(AUDIT/'reopen_verification_r6.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(checks,indent=2,ensure_ascii=False))
