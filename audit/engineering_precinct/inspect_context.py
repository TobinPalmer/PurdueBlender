import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for aid in ['mechanical_engineering','hovde_hall']:
    path=ROOT/'modular'/'manifest.json'
    import json
    manifest=json.loads(path.read_text(encoding='utf-8'))
    rec=next(a for a in manifest['assets'] if a['id']==aid)
    filepath=ROOT/'modular'/rec['file']
    with bpy.data.libraries.load(str(filepath),link=False) as (src,dst):
        dst.collections=[rec['collection']]
    col=dst.collections[0]
    print('BUILDING',aid,rec.get('placement_origin_xy_m'))
    if aid=='hovde_hall':
        print('PORTICO_OBJECTS',[ob.name for ob in col.all_objects if any(k in ob.name.lower() for k in ('column','portico','capital','cornice','rotunda'))])
    for ob in col.all_objects:
        if ob.type=='MESH':
            pts=[ob.matrix_world @ __import__('mathutils').Vector(corner) for corner in ob.bound_box]
            lo=[min(p[i] for p in pts) for i in range(3)]; hi=[max(p[i] for p in pts) for i in range(3)]
            if hi[0]-lo[0]>20 or hi[1]-lo[1]>20:
                print(ob.name,tuple(round(x,1) for x in lo),tuple(round(x,1) for x in hi))
