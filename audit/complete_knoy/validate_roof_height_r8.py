import bpy, json, hashlib, os
from mathutils import Vector
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET=ROOT+r'\modular\buildings\knoy_hall.blend'
OUT=ROOT+r'\audit\complete_knoy\roof_height_validation_r8.json'
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections.get('Asset_knoy_hall')
assert asset is not None
slab=bpy.data.objects.get('KNOY_FloorSlab_L5')
assert slab is not None and slab.get('story_status','').startswith('UNVERIFIED')
notes=bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
assert notes is not None
text=notes.as_string()
assert 'ROUND 8 — INDIANA 3DEP ROOF-SURFACE CHECK' in text
assert 'about 59.9 ft' in text
assert 'roof-level slab interpretation plausible' in text
# Mesh fingerprint for the saved state; the round-8 updater edits only object/scene/text properties.
h=hashlib.sha256(); meshes=[]
for o in sorted(asset.objects,key=lambda x:x.name):
 if o.type!='MESH': continue
 meshes.append(o.name)
 h.update(o.name.encode('utf-8'))
 for row in o.matrix_world:
  h.update(','.join(f'{v:.8f}' for v in row).encode('ascii'))
 for v in o.data.vertices:
  h.update(','.join(f'{c:.8f}' for c in v.co).encode('ascii'))
 for poly in o.data.polygons:
  h.update(','.join(str(i) for i in poly.vertices).encode('ascii'))
bounds={}
for n in ['KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5']:
 o=bpy.data.objects.get(n);assert o and o.type=='MESH'
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 bounds[n]={'min_z_m':min(p.z for p in pts),'max_z_m':max(p.z for p in pts),'min_z_ft':min(p.z for p in pts)*3.280839895,'max_z_ft':max(p.z for p in pts)*3.280839895}
report={
 'revision':8,'asset_reopened':'PASS','asset_path':'modular/buildings/knoy_hall.blend','asset_collection_object_count':len(asset.objects),'asset_mesh_count':len(meshes),'asset_mesh_geometry_sha256':h.hexdigest(),
 'l5_story_status':slab.get('story_status'),'l5_interpretation':slab.get('interpretation'),'model_slab_bounds':bounds,
 'l5_matches_assessed_datum_approx':abs(bounds['KNOY_FloorSlab_L5']['max_z_ft']-58.8)<0.1,
 'embedded_round8_evidence_note_present':True,'roof_height_assessment_json_present':os.path.isfile(ROOT+r'\audit\complete_knoy\roof_height_assessment_r8.json'),'vertical_evidence_svg_present':os.path.isfile(ROOT+r'\audit\complete_knoy\knoy_roof_height_vertical_evidence_r8.svg'),
 'tile_metadata_snapshot_present':os.path.isfile(ROOT+r'\audit\complete_knoy\indiana_3dep_knoy_tile_metadata_r8.json'),
 'vertical_evidence_preview_present':os.path.isfile(ROOT+r'\audit\complete_knoy\knoy_roof_height_vertical_evidence_r8_preview.png'),
 'mesh_or_placement_changes_made_by_round8_updater':False,
 'pv_alignment_status':'No PV transform fit; cyan bounds overlay remains retracted in r7 records and is excluded from r8 height analysis.',
 'scope':'Knoy-only saved source evidence metadata; no master/shared/other building files edited.'
}
assert report['asset_collection_object_count']==63
assert report['l5_matches_assessed_datum_approx']
assert report['roof_height_assessment_json_present'] and report['vertical_evidence_svg_present'] and report['tile_metadata_snapshot_present'] and report['vertical_evidence_preview_present']
with open(OUT,'w',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
print(json.dumps(report,indent=2))
