"""Technical inspection of reopened r04; no visual score and no source save."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector

D=Path(__file__).resolve().parent
P=Path(bpy.data.filepath)
sha=hashlib.sha256(P.read_bytes()).hexdigest()
C=bpy.data.collections['Asset_felix_haas_hall']
checks=[]
for o in C.all_objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    checks.append({'name':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces)})
    bm.free()
palette=[]
for m in bpy.data.materials:
    if not m.name.startswith(('HAAS_New_','HAAS_Detail_')):continue
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
    if not p:continue
    bricks=[n for n in m.node_tree.nodes if n.type=='TEX_BRICK']
    palette.append({'material':m.name,'color_space':'scene-linear RGB; not display sRGB','viewport_color':list(m.diffuse_color),'base_color':list(p.inputs['Base Color'].default_value),'roughness':p.inputs['Roughness'].default_value,'metallic':p.inputs['Metallic'].default_value,'procedural_masonry':[{'color1':list(n.inputs['Color1'].default_value),'color2':list(n.inputs['Color2'].default_value),'mortar_color':list(n.inputs['Mortar'].default_value),'brick_width_m':n.inputs['Brick Width'].default_value,'row_height_m':n.inputs['Row Height'].default_value,'mortar_size_m':n.inputs['Mortar Size'].default_value} for n in bricks]})
(D/'material_palette.json').write_text(json.dumps({'asset_sha256':sha,'method':'Visually estimated from user front photograph and multiple real exterior views; uncalibrated, not measured reflectance','materials':palette},indent=2)+'\n')
report={'asset_sha256':sha,'reopened_file':str(P),'expected_collection':C.name,'revision':C.get('revision'),'objects':len(C.all_objects),'bad_meshes':[x for x in checks if x['nonmanifold_edges'] or x['zero_area_faces']],'external_libraries':[x.filepath for x in bpy.data.libraries],'unpacked_external_images':[x.filepath for x in bpy.data.images if x.filepath and not x.packed_file],'source_saved':False,'visual_score':None,'accepted':False,'checks':checks}
assert not report['bad_meshes']
assert not report['external_libraries']
assert not report['unpacked_external_images']
assert C.get('revision')=='detail_color_r04'
assert hashlib.sha256(P.read_bytes()).hexdigest()==sha
(D/'reopen_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('asset_sha256','revision','objects','bad_meshes','external_libraries','unpacked_external_images','source_saved')}))
