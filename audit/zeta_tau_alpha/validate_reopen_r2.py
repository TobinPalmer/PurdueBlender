"""Fresh-process integrity and sign-placement checks for the frozen R2 library."""
import bpy, json, os, hashlib
from mathutils import Vector

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
PATH=os.path.join(ROOT,'modular','buildings','zeta_tau_alpha.blend')
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'reopen_validation_r2.json')
ASSET_ID='massing_zeta_tau_alpha_af8a443'
COLL='Asset_'+ASSET_ID
bpy.ops.wm.open_mainfile(filepath=PATH)
scene=bpy.data.scenes.get('Building_'+ASSET_ID)
asset=bpy.data.collections.get(COLL)
assert scene is not None, 'Expected building scene missing'
assert asset is not None, 'Expected stable export collection missing'
objects=list(asset.all_objects)
shell=bpy.data.objects.get('ZTA_Continuous_Red_Brick_Exterior_Shell')
assert shell is not None and shell.type=='MESH'
assert len(shell.data.vertices)>0 and len(shell.data.polygons)>0
images=[]
for img in bpy.data.images:
    if img.source=='FILE':
        images.append({'name':img.name,'filepath':img.filepath,
                       'packed':img.packed_file is not None,
                       'size_px':list(img.size)})
broken=[img for img in images if not img['packed'] and not os.path.exists(bpy.path.abspath(img['filepath']))]
assert not broken, 'Missing un-packed image dependency: '+repr(broken)
origin=list(asset.get('placement_origin_xy_m',(None,None)))
assert len(origin)==2 and all(v is not None for v in origin)

def world_bounds(obj):
    pts=[obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]

letters=bpy.data.objects.get('ZTA_Pediment_Letters')
plaque=bpy.data.objects.get('ZTA_Chapter_Name_Plaque')
pediment=bpy.data.objects.get('ZTA_Portico_Triangular_Pediment')
assert letters is not None and letters.type=='FONT' and letters.data.body=='ZTA'
assert plaque is not None and pediment is not None
letter_bounds=world_bounds(letters)
plaque_bounds=world_bounds(plaque)
pediment_bounds=world_bounds(pediment)
assert plaque_bounds[1][0] > pediment_bounds[1][1], 'Plaque is not outside the pediment face'
assert letter_bounds[1][0] > plaque_bounds[1][1]-0.005, 'Raised letters do not sit on the plaque face'
asset_max_z=max((obj.matrix_world @ Vector(corner)).z
                for obj in objects for corner in obj.bound_box)
assert abs(asset_max_z-11.91)<0.01, f'Unexpected asset max Z: {asset_max_z}'

report={
 'status':'PASS','file':os.path.relpath(PATH,ROOT).replace('\\','/'),
 'sha256':hashlib.sha256(open(PATH,'rb').read()).hexdigest(),
 'scene':scene.name,'export_collection':asset.name,
 'object_count':len(objects),'mesh_count':sum(o.type=='MESH' for o in objects),
 'material_count':len([m for m in bpy.data.materials if m.name.startswith('ZTA |')]),
 'shell_vertex_count':len(shell.data.vertices),'shell_polygon_count':len(shell.data.polygons),
 'shell_uv_layers':[uv.name for uv in shell.data.uv_layers],
 'shell_bounds_local_m':[[min((shell.matrix_world@Vector(c))[i] for c in shell.bound_box),
                          max((shell.matrix_world@Vector(c))[i] for c in shell.bound_box)] for i in range(3)],
 'placement_origin_xy_m':origin,'images':images,'broken_external_images':broken,
 'measured_asset_bbox_max_z_m':round(asset_max_z,2),
 'pediment_text':'ZTA','pediment_text_world_bounds_m':letter_bounds,
 'plaque_world_bounds_m':plaque_bounds,'pediment_world_bounds_m':pediment_bounds,
 'pediment_text_outward_side_check':'PASS','candidate_is_separate_from_master':not os.path.samefile(PATH,os.path.join(ROOT,'purdue_campus_master.blend'))
}
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print('ZTA_R2_REOPEN_VALIDATION',json.dumps(report,indent=2))
