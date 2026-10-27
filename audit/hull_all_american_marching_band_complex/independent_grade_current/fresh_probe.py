import bpy, json, os, math
from pathlib import Path
asset = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_hull_all_american_marching_band_complex_665bcb7.blend')
scene_name='Building_massing_hull_all_american_marching_band_complex_665bcb7'
coll_name='Asset_massing_hull_all_american_marching_band_complex_665bcb7'
out=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\hull_all_american_marching_band_complex\independent_grade_current\blender_probe.json')
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.data.scenes.get(scene_name); coll=bpy.data.collections.get(coll_name)
if not scene or not coll: raise RuntimeError('Expected scene or collection missing')
objs=[]; mats={}; meshless=[]; world=[]; vertex_samples=[]
for o in coll.objects:
    if o.type=='MESH':
        ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
        coords=[o.matrix_world @ v.co for v in me.vertices]
        if coords:
            bb=[[min(p[i] for p in coords) for i in range(3)],[max(p[i] for p in coords) for i in range(3)]]
            world.append(bb)
        else: bb=None
        names=[]
        for m in o.data.materials:
            if not m: names.append(None); continue
            mats[m.name]=mats.get(m.name,0)+1; names.append(m.name)
        if not o.data.materials: meshless.append(o.name)
        if len(objs)<80:
            objs.append({'name':o.name,'verts':len(me.vertices),'faces':len(me.polygons),'bounds':bb,'materials':names})
        if ('foundation' in o.name.lower() or 'shell' in o.name.lower() or 'footprint' in o.name.lower() or o.name=='Hull "All-American" Marching Band Complex'):
            vertex_samples.append({'name':o.name,'bounds':bb,'verts':len(me.vertices),'samples':[[round(v.co.x,4),round(v.co.y,4),round(v.co.z,4)] for v in list(me.vertices)[:30]]})
        ev.to_mesh_clear()
    elif o.type not in {'FONT'}:
        pass
external=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        external.append({'name':im.name,'path':im.filepath})
res={'asset':str(asset),'scene':scene.name,'collection':coll.name,'objects':len(coll.objects),'mesh_count':sum(o.type=='MESH' for o in coll.objects),'materialless_meshes':meshless,'external_images':external,'scene_unit_system':scene.unit_settings.system,'scene_unit_scale':scene.unit_settings.scale_length,'materials':mats,'all_mesh_world_bounds':[[[min(b[0][i] for b in world),min(b[0][i] for b in world),min(b[0][i] for b in world)] for i in range(3)],[max(b[1][i] for b in world) for i in range(3)]] if world else None,'sample_objects':objs,'footprint_related':vertex_samples}
out.write_text(json.dumps(res,indent=2),encoding='utf-8')
print('WROTE',out)
print(json.dumps({k:res[k] for k in ['objects','mesh_count','materialless_meshes','external_images','scene_unit_system','scene_unit_scale','materials','footprint_related']},indent=2))
