import bpy, importlib.util, json, os
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
MASTER=ROOT/'purdue_campus_master.blend'
MODULE=ROOT/'lighting'/'sunset_cloud_world.py'
spec=importlib.util.spec_from_file_location('sunset_cloud_world',MODULE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

scene=bpy.context.scene
libs=[(lib.name,bpy.path.abspath(lib.filepath)) for lib in bpy.data.libraries]
missing=[(name,path) for name,path in libs if not os.path.exists(path)]
if missing:
    raise RuntimeError(f'{len(missing)} linked building libraries are missing before edit: {missing[:5]}')
placements={ob.name:tuple(tuple(round(float(c),6) for c in row) for row in ob.matrix_world) for ob in bpy.data.objects if ob.name.startswith('Placement_')}
if len(placements)!=39:
    raise RuntimeError(f'Expected 39 placement markers, got {len(placements)}')

bounds=(-3600.0,3500.0,-2700.0,4100.0)
clouds,puffs=mod.install_campus_sunset(scene,bounds,spacing=950.0,seed=24731)
new_placements={ob.name:tuple(tuple(round(float(c),6) for c in row) for row in ob.matrix_world) for ob in bpy.data.objects if ob.name.startswith('Placement_')}
if placements!=new_placements:
    raise RuntimeError('Placement transforms changed during sunset installation')
missing=[(lib.name,bpy.path.abspath(lib.filepath)) for lib in bpy.data.libraries if not os.path.exists(bpy.path.abspath(lib.filepath))]
if len(bpy.data.libraries)!=len(libs) or missing:
    raise RuntimeError(f'Linked library set changed: before={len(libs)}, after={len(bpy.data.libraries)}, missing={missing[:5]}')
if clouds.name not in scene.objects or len(clouds.data.polygons)==0:
    raise RuntimeError('Cloud mesh is absent from the master scene or empty')

bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
print('MASTER_SAVED',json.dumps({'path':str(MASTER),'scene':scene.name,'libraries':len(libs),'missing_libraries':len(missing),'placement_markers':len(placements),'cloud_object':clouds.name,'cloud_puffs':puffs,'cloud_faces':len(clouds.data.polygons),'dome':bool(scene.objects.get('Campus Sunset Sky Dome')),'world':scene.world.name,'bounds_m':bounds,'time':scene['campus_time']}),flush=True)
