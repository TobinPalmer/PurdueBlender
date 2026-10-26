import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
master=root/'purdue_campus_master.blend'
mod=json.loads((root/'modular/manifest.json').read_text(encoding='utf-8'))
a=next(x for x in mod['assets'] if x['id']=='burton_morgan_center')
bpy.ops.wm.open_mainfile(filepath=str(master))
marker=bpy.data.objects.get('Placement_burton_morgan_center')
probes=[]
for o in bpy.data.objects:
    if o.type=='EMPTY' and o.instance_type=='COLLECTION' and o.instance_collection:
        if o.name=='Placement_burton_morgan_center' or 'burton_morgan' in o.name.lower() or 'Burton' in o.instance_collection.name:
            probes.append({'object':o.name,'instance_collection':o.instance_collection.name,'instance_location':list(o.location),'collection_library':o.instance_collection.library.filepath if o.instance_collection.library else None})
result={'master_opened':True,'master_file':'purdue_campus_master.blend','marker_found':marker is not None,'marker_location':list(marker.location) if marker else None,'placement_origin_manifest':a.get('placement_origin_xy_m'),'candidate_instances':probes,'note':'Read-only probe. No master edits performed.'}
(root/'audit/burton_morgan_center_independent_grade/master_probe.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
