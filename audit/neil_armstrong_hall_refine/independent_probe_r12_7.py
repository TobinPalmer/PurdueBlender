import bpy, hashlib, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/neil_armstrong_hall.blend'
OUT=ROOT/'audit/neil_armstrong_hall_refine/independent_probe_r12_7.json'
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get('Asset_neil_armstrong_hall')
root=bpy.data.objects.get('AssetRoot_neil_armstrong_hall')
objs=list(col.objects) if col else []
meshes=[o for o in objs if o.type=='MESH']
no_mats=[o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
null_slots=[o.name for o in meshes if any(m is None for m in o.data.materials)]
missing_images=[]
for im in bpy.data.images:
 if im.source=='FILE' and not (im.packed_file or os.path.exists(bpy.path.abspath(im.filepath))): missing_images.append(im.name)
canopy=bpy.data.objects.get('ARMS_Cantilever_Canopy_Deck')
pts=[canopy.matrix_world@v.co for v in canopy.data.vertices] if canopy else []
report={'asset':str(ASSET),'sha256':sha,'fresh_blender_open':True,'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,'collection_present':bool(col),'collection_object_count':len(objs),'scene_object_count':len(bpy.data.objects),'mesh_object_count':len(meshes),'root_location':[float(x) for x in root.location] if root else None,'root_matrix_world':[[round(float(x),6) for x in row] for row in root.matrix_world] if root else None,'canopy_present':bool(canopy),'canopy_vertices':len(canopy.data.vertices) if canopy else None,'canopy_faces':len(canopy.data.polygons) if canopy else None,'canopy_world_bounds':{'min':[round(min(p[i] for p in pts),3) for i in range(3)],'max':[round(max(p[i] for p in pts),3) for i in range(3)]} if pts else None,'meshes_without_material':no_mats,'meshes_with_null_slots':null_slots,'missing_external_images':missing_images,'all_meshes_materialed':not no_mats and not null_slots,'portable_images':not missing_images}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
