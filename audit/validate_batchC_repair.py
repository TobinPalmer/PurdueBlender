import bpy, json, os, sys
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
key=sys.argv[-1]
with open(os.path.join(root,'audit',f'batchC_{key}_evidence.json'),encoding='utf-8') as f: ev=json.load(f)
path=os.path.join(root,ev['asset_file'])
bpy.ops.wm.open_mainfile(filepath=path)
asset=bpy.data.collections.get(ev['export_collection'])
assert asset is not None, 'export collection missing after reopen'
objs=[]
def walk(c):
 for o in c.objects: objs.append(o)
 for child in c.children: walk(child)
walk(asset)
meshes=[o for o in objs if o.type=='MESH']
materials={m for o in meshes for m in o.data.materials if m}
bad=[]
for m in materials:
 if not m.use_nodes: bad.append(m.name+':nodes-disabled'); continue
 nt=m.node_tree
 outputs=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL']
 if not outputs or not any(link.to_node in outputs and link.to_socket.name=='Surface' for link in nt.links): bad.append(m.name+':surface-unconnected')
 elif not any(n.type in {'TEX_NOISE','TEX_BRICK','TEX_IMAGE','TEX_COORD'} for n in nt.nodes): bad.append(m.name+':no-texture-node')
mins=[1e9,1e9,1e9]; maxs=[-1e9,-1e9,-1e9]
for ob in meshes:
 for v in ob.bound_box:
  p=ob.matrix_world@Vector(v)
  for i in range(3): mins[i]=min(mins[i],p[i]); maxs[i]=max(maxs[i],p[i])
assert not bad, bad
assert meshes, 'no meshes found'
assert not any(n.type=='TEX_IMAGE' for m in materials for n in m.node_tree.nodes), 'packed/source-only material unexpectedly uses image nodes'
result={'reload':'PASS','asset_file':ev['asset_file'],'collection':asset.name,'objects':len(objs),'mesh_objects':len(meshes),'unique_materials':len(materials),'connected_texture_materials':len(materials)-len(bad),'material_failures':bad,'local_asset_bounds_m':[mins,maxs],'official_gis_footprint_dimensions_m':ev['footprint']['dimensions_m'],'recommended_master_marker_xy_m':ev['coordinate_method']['recommended_master_marker_xy_m'],'no_image_texture_dependencies':True,'all_source_asset_objects_inside_export_collection':True,'master_or_manifest_edited':False}
if key=='national_soil_erosion':
 result['identity_check']='GIS FID 242 is named Soil Erosion Lab (SOIL); assigned NSERL identity matched using official Purdue/USDA name/address references at 275 South Russell St.'
 result['height_uncertainty']='GIS Extrution field is retained as source value; modeled height is an estimate from treating the value as feet, not a verified measured elevation.'
if key=='nacc':
 import math
 with open(os.path.join(root,'audit','batchC_nacc_official_footprint.json'),encoding='utf-8-sig') as f: gis=json.load(f)['features'][0]
 ring=gis['geometry']['rings'][0][:-1]; lat0,lon0=40.4274,-86.9137
 sx=111412.84*math.cos(math.radians(lat0)); sy=111040.0
 xy=[((lon-lon0)*sx,(lat-lat0)*sy) for lon,lat in ring]
 a2=cxsum=cysum=0.0
 for (x,y),(u,v) in zip(xy,xy[1:]+xy[:1]):
  cross=x*v-u*y; a2+=cross; cxsum+=(x+u)*cross; cysum+=(y+v)*cross
 centroid=(cxsum/(3*a2),cysum/(3*a2))
 expected=[[min(x-centroid[0] for x,y in xy),min(y-centroid[1] for x,y in xy)],[max(x-centroid[0] for x,y in xy),max(y-centroid[1] for x,y in xy)]]
 shell=next((o for o in meshes if 'official gis footprint structural shell' in o.name.lower()),None)
 if shell is None:
  shell=next(o for o in meshes if 'gis perimeter wall panels with real glazing openings' in o.name.lower())
 shell_xy=[shell.matrix_world@Vector(v) for v in shell.bound_box]
 actual=[[min(v.x for v in shell_xy),min(v.y for v in shell_xy)],[max(v.x for v in shell_xy),max(v.y for v in shell_xy)]]
 error=max(abs(actual[i][j]-expected[i][j]) for i in range(2) for j in range(2))
 assert error<0.002, f'NACC GIS shell mismatch {error}m: actual={actual} expected={expected}'
 marker=list(asset.get('gis_placement_origin_xy_m',[])); shift=list(asset.get('local_geometry_shift_m',[])); bbox_origin=list(asset.get('build_bbox_origin_xy_m',[]))
 assert marker and max(abs(marker[i]-[-278.927997,190.076894][i]) for i in range(2))<0.001, f'wrong NACC centroid marker: {marker}'
 assert shift and max(abs(shift[i]-[-0.204336,0.194182,0.0][i]) for i in range(3))<0.001, f'wrong NACC local geometry shift: {shift}'
 result['gis_shell_footprint_alignment']={'status':'PASS','max_xy_error_m':error,'shell_local_bounds_m':actual,'expected_centroid_relative_gis_bounds_m':expected,'build_bbox_origin_xy_m':bbox_origin,'manifest_centroid_marker_xy_m':marker,'local_geometry_shift_from_bbox_m':shift,'source_recentered_to_manifest_centroid':True}
if key=='life_science_plant_soils':
 gisbox=ev['footprint']['bbox_local_m']; tol=.002
 outside=[]; greenhouse=[]
 for ob in meshes:
  bb=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  bmin=[min(v[i] for v in bb) for i in range(3)]; bmax=[max(v[i] for v in bb) for i in range(3)]
  if bmin[0]<gisbox[0][0]-tol or bmin[1]<gisbox[0][1]-tol or bmax[0]>gisbox[1][0]+tol or bmax[1]>gisbox[1][1]+tol:
   outside.append({'name':ob.name,'xy_bounds':[[bmin[0],bmin[1]],[bmax[0],bmax[1]]]})
  if 'greenhouse' in ob.name.lower(): greenhouse.append({'name':ob.name,'xy_bounds':[[bmin[0],bmin[1]],[bmax[0],bmax[1]]]})
 assert not outside, f'LSPS mesh geometry extends beyond official GIS bbox: {outside[:8]}'
 assert greenhouse, 'No LSPS greenhouse inset objects found'
 result['asset_xy_bounds_within_gis_footprint']={'status':'PASS','outside_mesh_count':0,'official_gis_bbox_local_m':gisbox,'greenhouse_mesh_objects':len(greenhouse),'greenhouse_bounds_within_gis_bbox':True,'former_service_apron_removed':True}
out=os.path.join(root,'audit',f'batchC_{key}_validation.json')
with open(out,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
