"""Independent structural inspection only. Does not save any Blender library."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector

D=Path(__file__).resolve().parent
ROOT=D.parents[3]
args=sys.argv[sys.argv.index('--')+1:]
which=args[0]
path=ROOT/'modular/buildings/felix_haas_hall.blend' if which=='current' else ROOT/'.git/lfs/objects/0d/e3/0de3417c6cc3af247b2100242720d39871bc8ed188dcf06bfbb96d9bead2c067'
bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
C=bpy.data.collections.get('Asset_felix_haas_hall')
assert C
rows=[]
for o in C.all_objects:
    if not o:continue
    coordinates=[tuple(round(float(x),7) for x in v.co) for v in o.data.vertices] if o.type=='MESH' else []
    faces=[tuple(p.vertices) for p in o.data.polygons] if o.type=='MESH' else []
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    bounds=[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
    rows.append({'name':o.name,'type':o.type,'mesh_sha256':hashlib.sha256(json.dumps([coordinates,faces]).encode()).hexdigest(),'matrix':[[float(x) for x in r] for r in o.matrix_world],'bounds':bounds,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'render_hidden':o.hide_render,'modifiers':[(m.name,m.type) for m in o.modifiers]})
data={'asset_path':str(path),'asset_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'expected_collection_present':True,'collection_name':C.name,'objects':rows,'count':len(rows),'libraries':[x.filepath for x in bpy.data.libraries],'images':[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images],'scene_names':[s.name for s in bpy.data.scenes],'library_saved':False}
(D/f'{which}_inspection.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('INDEPENDENT_INSPECTION',which,data['asset_sha256'],data['count'])
