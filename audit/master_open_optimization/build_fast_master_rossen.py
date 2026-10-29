import bpy,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit'/'master_open_optimization'
SOURCE=OUT/'purdue_campus_master_fast.blend'
OUTPUT=OUT/'purdue_campus_master_fast_rossen.blend'
revisions=json.loads((OUT/'rossen_source_revisions.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
libs=[lib for lib in bpy.data.libraries if 'campus_proxy_library.blend' in lib.filepath]
if len(libs)!=1: raise RuntimeError(f'Expected one existing proxy library; got {len(libs)}')
libs[0].filepath='//campus_proxy_library_rossen.blend'
for row in revisions:
    c=bpy.data.collections.get('Asset_'+row['id'])
    if c is None: raise RuntimeError('Missing linked collection Asset_'+row['id'])
scene['rossen_source_revisions_json']=json.dumps(revisions,separators=(',',':'))
scene['proxy_library']='campus_proxy_library_rossen.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
report={'status':'PASS','master_file':str(OUTPUT),'proxy_library':libs[0].filepath,'asset_count':scene.get('source_asset_count'),'library_count':len(bpy.data.libraries),'source_revisions':revisions}
(OUT/'fast_master_rossen_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('FAST_MASTER_ROSSEN_COMPLETE '+json.dumps(report),flush=True)
