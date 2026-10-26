import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

asset = Path(sys.argv[-2]).resolve()
out = Path(sys.argv[-1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene=bpy.context.scene
asset_col=next((c for c in bpy.data.collections if c.name.startswith('Asset_massing_cary_quadrangle_northeast_cqne_0a76fca')),None)
objects=list(asset_col.all_objects) if asset_col else []
rows=[]
allcoords=[]
for o in objects:
    row={'name':o.name,'type':o.type,'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale),'modifiers':[m.name for m in o.modifiers],'materials':[m.name for m in getattr(o.data,'materials',[]) if m]}
    if o.type=='MESH':
        ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        me=ev.to_mesh()
        coords=[o.matrix_world @ v.co for v in me.vertices]
        allcoords.extend(coords)
        row.update({'vertices':len(me.vertices),'polygons':len(me.polygons),'evaluated_vertex_count':len(coords),'evaluated_bounds':[[min(p[i] for p in coords) for i in range(3)],[max(p[i] for p in coords) for i in range(3)]] if coords else None})
        ev.to_mesh_clear()
    rows.append(row)
if allcoords:
    bounds=[[min(p[i] for p in allcoords) for i in range(3)],[max(p[i] for p in allcoords) for i in range(3)]]
else: bounds=None
# Topology probe on primary GIS wall shell: number of boundary/nonmanifold edges.
primary=next((o for o in objects if o.name=='CQNE | GIS footprint walls' and o.type=='MESH'),None)
topo={}
if primary:
    me=primary.data
    edge_use={tuple(sorted(e.vertices)):0 for e in me.edges}
    for poly in me.polygons:
        for k in range(poly.loop_total):
            edge=tuple(sorted((me.loops[poly.loop_start+k].vertex_index,me.loops[poly.loop_start+(k+1)%poly.loop_total].vertex_index)))
            edge_use[edge]=edge_use.get(edge,0)+1
    topo={'verts':len(me.vertices),'faces':len(me.polygons),'boundary_edges':sum(v==1 for v in edge_use.values()),'edges_more_than_two_faces':sum(v>2 for v in edge_use.values()),'bottom_vertex_count':sum(abs(v.co.z)<1e-5 for v in me.vertices),'top_vertex_count':sum(abs(v.co.z-12.5)<1e-5 for v in me.vertices)}
# Direct raw GIS ring versus the independently reopened structural wall vertices.
source_path=Path(__file__).resolve().parents[1]/'massing_cary_quadrangle_northeast_cqne_0a76fca'/'sources'/'purdue_gis_feature_638_cqne_4326.json'
source=json.loads(source_path.read_text(encoding='utf-8'))['features'][0]
ring=source['geometry']['rings'][0]
lat0=40.4274; lon0=-86.9137; xscale=111412.84*math.cos(math.radians(lat0)); yscale=111040.0
source_xy=[((lon-lon0)*xscale,(lat-lat0)*yscale) for lon,lat in ring]
if len(source_xy)>1 and math.dist(source_xy[0],source_xy[-1])<0.005: source_xy.pop()
wall_xy=[]
if primary:
    wall_xy=[tuple((primary.matrix_world @ v.co)[:2]) for v in primary.data.vertices if abs(v.co.z)<1e-5]
nearest=[min(math.dist(p,q) for q in wall_xy) for p in source_xy] if wall_xy else []
gis_check={'source_feature_id':source['attributes']['FID'],'source_ring_unique_vertices':len(source_xy),'wall_bottom_vertex_count':len(wall_xy),'max_source_vertex_to_wall_nearest_m':max(nearest) if nearest else None,'mean_source_vertex_to_wall_nearest_m':sum(nearest)/len(nearest) if nearest else None,'source_bounds':[[min(p[0] for p in source_xy),min(p[1] for p in source_xy)],[max(p[0] for p in source_xy),max(p[1] for p in source_xy)]],'wall_bounds':[[min(p[0] for p in wall_xy),min(p[1] for p in wall_xy)],[max(p[0] for p in wall_xy),max(p[1] for p in wall_xy)]] if wall_xy else None}
# Fresh isolated preview render from reopened asset.
if bounds:
    center=Vector(tuple((bounds[0][i]+bounds[1][i])/2 for i in range(3)))
    dims=Vector(tuple(bounds[1][i]-bounds[0][i] for i in range(3)))
    cam_data=bpy.data.cameras.new('Independent grade camera')
    cam=bpy.data.objects.new('Independent grade camera',cam_data); scene.collection.objects.link(cam)
    cam.location=center+Vector((dims.x*0.75,-dims.x*0.85,dims.z*1.2))
    direction=center-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    cam_data.type='ORTHO'; cam_data.ortho_scale=max(dims.x,dims.y)*1.35
    scene.camera=cam
    scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(out/'independent_reopen_preview.png')
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
    bpy.ops.render.render(write_still=True)
scene.camera=None
result={'asset':str(asset),'blender_version':bpy.app.version_string,'active_scene':scene.name,'expected_collection_present':asset_col is not None,'object_count':len(objects),'objects':rows,'world_bounds_m':bounds,'world_dimensions_m':[bounds[1][i]-bounds[0][i] for i in range(3)] if bounds else None,'primary_wall_topology':topo,'gis_footprint_check':gis_check,'external_images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]}
out.mkdir(parents=True,exist_ok=True)
(out/'blender_probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('INDEPENDENT_PROBE='+json.dumps(result,sort_keys=True))





