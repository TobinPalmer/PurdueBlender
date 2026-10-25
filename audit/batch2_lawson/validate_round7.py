import bpy, json, math, os
from mathutils import Vector

ASSET = r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/lawson_hall.blend'
GIS_SNAPSHOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/gis_fid59_live.json'
GIS_PROJECT = r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/target_buildings_gis.json'
OUT = r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/validation_round7.json'
EDGES_OUT = r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch2_lawson/r7_shell_edges_round7.json'
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset=bpy.data.collections.get('Asset_lawson_hall'); root=bpy.data.objects.get('AssetRoot_lawson_hall')
assert asset and root and bpy.data.filepath.lower().endswith('lawson_hall.blend')
objs=[o for o in asset.all_objects if o]; meshes=[o for o in objs if o.type=='MESH']
mesh_coords=[]
for ob in meshes:
    mesh_coords.extend(ob.matrix_world @ Vector(v) for v in ob.bound_box)
bounds={axis:[min(getattr(v,axis) for v in mesh_coords),max(getattr(v,axis) for v in mesh_coords)] for axis in ('x','y','z')}
unmaterialed=[o.name for o in meshes if not o.data.materials]
missing_images=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and im.filepath and not os.path.exists(bpy.path.abspath(im.filepath))]
identity=all(abs(root.matrix_world[i][j]-(1 if i==j else 0))<1e-7 for i in range(4) for j in range(4))

def obj_edges(names):
    out=[]
    for name in names:
        ob=bpy.data.objects.get(name)
        if not ob or ob.type!='MESH': continue
        vv=[ob.matrix_world@v.co for v in ob.data.vertices]
        zmin=min(v.z for v in vv)
        for e in ob.data.edges:
            a,b=vv[e.vertices[0]],vv[e.vertices[1]]
            if abs(a.z-zmin)<1e-4 and abs(b.z-zmin)<1e-4:
                out.append(((a.x,a.y),(b.x,b.y)))
    return out
base_edges=obj_edges(['LWSN_Exterior_Brick','LWSN_Rotunda_Curtain_Glass'])
r7_names=[o.name for o in meshes if o.name.startswith('LWSN_R7_Vestibule_Glass_') or o.name.startswith('LWSN_R7_Vestibule_Door_Leaf_') or o.name=='LWSN_R7_North_GIS_Footprint_Closure']
r7_edges=obj_edges(r7_names)
edge_snapshot={}
for name in ['LWSN_Exterior_Brick','LWSN_Rotunda_Curtain_Glass','LWSN_R7_North_GIS_Footprint_Closure']+r7_names:
    ob=bpy.data.objects.get(name)
    if not ob or ob.type!='MESH': continue
    vv=[ob.matrix_world@v.co for v in ob.data.vertices]; zmin=min(v.z for v in vv)
    ed=[]
    for e in ob.data.edges:
        a,b=vv[e.vertices[0]],vv[e.vertices[1]]
        if abs(a.z-zmin)<1e-4 and abs(b.z-zmin)<1e-4: ed.append([[round(a.x,6),round(a.y,6)],[round(b.x,6),round(b.y,6)]])
    edge_snapshot[name]={'z0_m':round(zmin,6),'edges':ed}
with open(EDGES_OUT,'w',encoding='utf8') as f: json.dump(edge_snapshot,f,indent=2)
gis=json.load(open(GIS_PROJECT,encoding='utf8'))['LWSN']['world_polygon']
ring=[(p[0]+282.5,p[1]-44.0) for p in gis]

def point_segment_dist(p,s):
    a,b=s; dx=b[0]-a[0];dy=b[1]-a[1]; den=dx*dx+dy*dy
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
    return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))

def boundary_coverage(edges):
    vals=[]; per_edge=[]
    for i,a in enumerate(ring):
        b=ring[(i+1)%len(ring)]
        local=[]
        for j in range(21):
            t=j/20
            p=(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t)
            d=min(point_segment_dist(p,s) for s in edges) if edges else 999
            vals.append(d);local.append(d)
        per_edge.append({'gis_edge_index':i,'length_m':math.dist(a,b),'max_nearest_distance_m':max(local),'mean_nearest_distance_m':sum(local)/len(local),'fraction_within_0_10m':sum(d<=.10 for d in local)/len(local)})
    worst=sorted(per_edge,key=lambda x:x['max_nearest_distance_m'],reverse=True)[:5]
    return {'sample_points':len(vals),'within_0_10m':sum(d<=.10 for d in vals),'fraction_within_0_10m':sum(d<=.10 for d in vals)/len(vals),'max_nearest_distance_m':max(vals),'mean_nearest_distance_m':sum(vals)/len(vals),'worst_gis_edges':worst}

# Reproject raw live GIS longitude/latitude using the project's published local tangent approximation.
raw=json.load(open(GIS_SNAPSHOT,encoding='utf8'))['features'][0]['geometry']['rings'][0]
def project(pt): return ((pt[0]+86.9137)*111412.84*math.cos(math.radians(40.4274)),(pt[1]-40.4274)*111040.0)
source_points=[project(p) for p in raw]
stored=json.load(open(GIS_PROJECT,encoding='utf8'))['LWSN']['world_polygon']
gis_deltas=[math.hypot(source_points[i][0]-stored[i][0],source_points[i][1]-stored[i][1]) for i in range(min(len(source_points),len(stored)))]

wall=bpy.data.objects.get('LWSN_1130_Harris_Video_Wall')
brick=bpy.data.materials.get('LWSN_Purdue_Red_Brick')
brick_connected=False
if brick and brick.node_tree:
    base=next((n for n in brick.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    brick_connected=bool(base and any(l.to_node==base and l.to_socket==base.inputs['Base Color'] and l.from_node.type=='TEX_BRICK' for l in brick.node_tree.links))
result={
 'source_asset':ASSET,'reopened_saved_source':os.path.normcase(os.path.abspath(bpy.path.abspath(bpy.data.filepath)))==os.path.normcase(os.path.abspath(ASSET)),
 'export_collection':'Asset_lawson_hall','export_objects':len(objs),'mesh_count':len(meshes),'root_transform_identity':identity,'root_world_matrix':[list(r) for r in root.matrix_world],
 'bounds_m':bounds,'unmaterialed_meshes':unmaterialed,'missing_external_images':missing_images,'brick_texture_drives_base_color':brick_connected,
 'live_GIS_FID59_vs_project_polygon':{'raw_source_ring_vertices':len(raw),'stored_project_ring_vertices':len(stored),'mean_vertex_delta_m':sum(gis_deltas)/len(gis_deltas),'max_vertex_delta_m':max(gis_deltas),'projected_using':'X=(lon+86.9137)*111412.84*cos(radians(40.4274); Y=(lat-40.4274)*111040'},
 'GIS_boundary_samples_vs_existing_structural_shell':boundary_coverage(base_edges),'GIS_boundary_samples_vs_shell_plus_R7_vestibule':boundary_coverage(base_edges+r7_edges),
 'GIS_shell_coverage_method':'21 evenly spaced samples on each of 54 ordered GIS boundary edges, compared to XY lower baseline edges from LWSN_Exterior_Brick, LWSN_Rotunda_Curtain_Glass, R7 GIS vestibule glass/door panels, and the R7 north-edge closure; 0.10 m tolerance.',
 'R7_vestibule_glass_and_door_objects':len(r7_names),'vestibule_canopy_exists':bpy.data.objects.get('LWSN_R7_Entrance_Canopy') is not None,
 'plan_registration_controls':{'pdf_pixels':[[323,86],[627,86],[298,986]],'project_local_m':[[-13.209,40.611],[14.791,40.547],[-15.553,-42.493]],'scale_m_per_pixel':[0.092105,0.0923377778],'uncertainty_m':'Approx. 0.3 m from raster edge-pick/line-width limits; not surveyed.'},
 'video_wall_reported_dimensions_m':list(wall.dimensions) if wall else None,'video_wall_module_count':sum(o.name.startswith('LWSN_R5_VideoWall_LCD_') for o in objs),
 'model_roof_max_z_m':bounds['z'][1],'roof_height_verified':False,'upper_floor_plans_verified':False,'continuous_stair_route_verified':False,'temporary_preview_cameras_saved':any(o.name.startswith('LWSN_R7_TEMP_') for o in bpy.data.objects),
 'remaining_issues':['No measured/current elevation or complete upper-floor plan found.','GIS attributes NUM_LEVELS and Extrution do not expose a documented measurement method or usable unit for roof height.','Canopy height, projection, entrance glazing, door width and mullion dimensions remain visual/illustrative estimates.','Façade opening cadence and upper-floor stair continuity remain unverified.']
}
with open(OUT,'w',encoding='utf8') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
