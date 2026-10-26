import bpy, json, math, hashlib, sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
asset=Path(args[0]).resolve(); out=Path(args[1]).resolve(); root=Path(args[2]).resolve()
manifest=json.loads((root/'modular'/'manifest.json').read_text(encoding='utf-8'))
entry=next(x for x in manifest['assets'] if x.get('id')=='birck_nanotechnology_center')
feature=json.loads((root/'audit'/'birck_nanotechnology_center'/'sources'/'purdue_gis_feature_604_raw.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene; col=bpy.data.collections.get(entry['collection'])
if col is None: raise RuntimeError('manifest export collection missing')
# Project source ring from EPSG:4326 into the repository's local frame using manifest origin only.
origin=entry['placement_origin_xy_m']; lon0=-86.9137; lat0=40.4274
mx=111412.84*math.cos(math.radians(lat0)); my=111040.0
coords=feature['geometry']['rings'][0]
if len(coords)>1 and math.dist(coords[0][:2],coords[-1][:2])<1e-12: coords=coords[:-1]
gis_local=[((lon-lon0)*mx-origin[0],(lat-lat0)*my-origin[1]) for lon,lat,*_ in coords]
shell=col.objects.get('Birck • full GIS-footprint research block')
if shell is None: raise RuntimeError('source-derived shell missing')
dg=bpy.context.evaluated_depsgraph_get(); ev=shell.evaluated_get(dg); mesh=ev.to_mesh()
try: shellpts=[ev.matrix_world@v.co for v in mesh.vertices]
finally: ev.to_mesh_clear()
zmin=min(p.z for p in shellpts); model_local=[]; _seen=set()
for p in shellpts:
    if abs(p.z-zmin)<1e-5:
        q=(round(p.x,6),round(p.y,6))
        if q not in _seen: model_local.append(q); _seen.add(q)
# symmetric directed vertex-to-polyline distance, plus polygon areas / perimeters
def point_seg_dist(p,a,b):
    vx=b[0]-a[0]; vy=b[1]-a[1]; den=vx*vx+vy*vy
    t=0.0 if den==0 else max(0.0,min(1.0,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/den))
    return math.dist(p,(a[0]+t*vx,a[1]+t*vy))
def ring_dists(pnts,ring):
    segs=list(zip(ring,ring[1:]+ring[:1]))
    return [min(point_seg_dist(p,a,b) for a,b in segs) for p in pnts]
def signed_area(r): return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]+r[:1]))*.5
def perim(r): return sum(math.dist(a,b) for a,b in zip(r,r[1:]+r[:1]))
a=ring_dists(gis_local,model_local); b=ring_dists(model_local,gis_local)
haus=max(max(a),max(b)); rms=math.sqrt((sum(x*x for x in a+b))/len(a+b))
# Reconstruct model perimeter in campus/project coordinates using manifest origin.
model_world=[(x+origin[0],y+origin[1]) for x,y in model_local]
# evaluate all collection mesh geometry bounds and portable dependencies
allpts=[]; types={}; object_names=[]; modifiers=[]
for o in col.objects:
    types[o.type]=types.get(o.type,0)+1; object_names.append(o.name)
    if o.type=='MESH':
        e=o.evaluated_get(dg); m=e.to_mesh()
        try: allpts.extend([e.matrix_world@v.co for v in m.vertices])
        finally: e.to_mesh_clear()
    if o.modifiers: modifiers.append({'name':o.name,'types':[m.type for m in o.modifiers]})
mins=[min(p[i] for p in allpts) for i in range(3)]; maxs=[max(p[i] for p in allpts) for i in range(3)]
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
libraries=[lib.filepath for lib in bpy.data.libraries if lib.filepath]
font_files=[{'name':font.name,'filepath':font.filepath,'packed':bool(font.packed_file)} for font in bpy.data.fonts]
scene_camlight=[o.name for o in scene.objects if o.type in {'CAMERA','LIGHT'}]
# Fresh named collection-only export, independent of the builder's existing export file.
export=out.with_name(out.stem+'_collection_export.blend')
bpy.data.libraries.write(str(export),{col},path_remap='RELATIVE')
listed=set(entry.get('objects',[])); actual=set(object_names)
result={
 'asset_path':str(asset),'asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,
 'scene':scene.name,'collection':col.name,'scene_object_count':len(scene.objects),'manifest':{'id':entry.get('id'),'kind':entry.get('kind'),'file':entry.get('file'),'scene':entry.get('scene'),'collection':entry.get('collection'),'placement_origin_xy_m':origin,'object_count':entry.get('object_count'),'manifest_name_count':len(listed),'asset_object_count':len(actual),'names_match_exactly':listed==actual,'missing_names':sorted(listed-actual),'unlisted_names':sorted(actual-listed)},
 'gis_feature':{'fid':feature['attributes'].get('FID'),'abbr':feature['attributes'].get('BLDG_ABBR'),'name':feature['attributes'].get('BUILDING_N'),'address':feature['attributes'].get('ADDRESS'),'spatial_reference':'EPSG:4326 (as documented in evidence.json; snapshot is raw feature geometry)','source_ring_vertex_count':len(gis_local)},
 'footprint':{'source_ring_vertex_count':len(gis_local),'model_shell_base_vertex_count':len(model_local),'symmetric_point_to_polyline_hausdorff_m':haus,'point_to_polyline_rms_m':rms,'model_shell_base_z_local_m':zmin,'source_area_m2':abs(signed_area(gis_local)),'model_area_m2':abs(signed_area(model_local)),'area_relative_error':abs(abs(signed_area(model_local))-abs(signed_area(gis_local)))/abs(signed_area(gis_local)),'source_perimeter_m':perim(gis_local),'model_perimeter_m':perim(model_local),'source_bounds_local_m':[[min(p[i] for p in gis_local),max(p[i] for p in gis_local)] for i in (0,1)],'model_bounds_local_m':[[min(p[i] for p in model_local),max(p[i] for p in model_local)] for i in (0,1)],'source_bounds_world_m':[[min(p[i]+origin[i] for p in gis_local),max(p[i]+origin[i] for p in gis_local)] for i in (0,1)]},
 'evaluated_collection_bounds_local_m':[[mins[i],maxs[i]] for i in (0,1,2)],'export_object_types':types,'object_names':sorted(object_names),'modifiers':modifiers,'scene_cameras_lights':sorted(scene_camlight),'collection_cameras_lights':[o.name for o in col.objects if o.type in {'CAMERA','LIGHT'}],'unpacked_external_images':external,'linked_libraries':libraries,'fonts':font_files,
 'independent_collection_export':{'path':str(export),'exists':export.exists(),'bytes':export.stat().st_size if export.exists() else None},
 'builder_evidence_present':(root/'audit'/'birck_nanotechnology_center'/'evidence.json').is_file()}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('asset_path','asset_sha256','manifest','gis_feature','footprint','evaluated_collection_bounds_local_m','export_object_types','collection_cameras_lights','unpacked_external_images','linked_libraries','independent_collection_export')},indent=2),flush=True)
