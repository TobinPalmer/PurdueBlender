import bpy,json,pathlib,shutil,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');D=P/'audit/walc_north';m=json.loads((P/'modular/manifest.json').read_text());ref=json.loads((P/'audit/official_building_references.json').read_text());a=next(a for a in m['assets'] if a['id']=='elliott_hall_of_music');path=P/'modular'/a['file'];shutil.copy2(path,D/'elliott_before.blend');bpy.ops.wm.open_mainfile(filepath=str(path));col=bpy.data.collections[a['collection']];old=list(col.all_objects)
legacy=bpy.data.collections.new('ELLT_Legacy_PreGIS_Reference_HIDDEN');bpy.context.scene.collection.children.link(legacy)
for child in list(col.children):col.children.unlink(child);legacy.children.link(child)
for o in list(col.objects):col.objects.unlink(o);legacy.objects.link(o)
legacy.hide_render=True;legacy.hide_viewport=True
origin=a['placement_origin_xy_m'];b=next(b for b in ref['buildings'] if b['code']=='ELLT');ring=b['rings_xy_m'][0][:-1];pts=[(x-origin[0],y-origin[1])for x,y in ring];N=len(pts);h=22.5
verts=[(x,y,z)for z in [0,h] for x,y in pts];faces=[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
mesh=bpy.data.meshes.new('ELLT_Official_Perimeter_Mesh');mesh.from_pydata(verts,[],faces);mesh.update();wall=bpy.data.objects.new('ELLT_Official_Footprint_Exterior_Walls',mesh);col.objects.link(wall)
mat=bpy.data.materials.get('ELLT_Indiana_Limestone') or next((x for x in bpy.data.materials if 'stone' in x.name.lower()),None)
if mat:mesh.materials.append(mat)
roofpts=[Vector((x,y,h))for x,y in pts];tris=tessellate_polygon([roofpts]);lookup={(v.x,v.y,v.z):i for i,v in enumerate(roofpts)};roofmesh=bpy.data.meshes.new('ELLT_Official_Roof_Plan_Mesh');roofmesh.from_pydata(roofpts,[],[tuple(t) if isinstance(t[0], int) else tuple(lookup[tuple(v)]for v in t)for t in tris]);roofmesh.update();roof=bpy.data.objects.new('ELLT_Official_Footprint_Roof_Estimated_22_5m',roofmesh);col.objects.link(roof)
roofmat=next((x for x in bpy.data.materials if 'roof' in x.name.lower()),None)
if roofmat:roofmesh.materials.append(roofmat)
wall['source_fid']=b['fid'];wall['horizontal_status']='Exact official perimeter registration using project coordinate transform';wall['height_status']='22.5m inherited main auditorium estimate; not measured';col['review_note']='Horizontal shell corrected; legacy facade/site/interior retained hidden because incompatible with official plan. Height and architectural details unverified.'
bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));c=bpy.data.collections[a['collection']];assert len(c.all_objects)==2
# Every perimeter vertex must recover official campus coordinates within Blender float precision.
w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls'];err=max(math.dist((w.data.vertices[i].co.x+origin[0],w.data.vertices[i].co.y+origin[1]),ring[i])for i in range(N));assert err<.0001
(D/'correction.json').write_text(json.dumps({'id':a['id'],'source':ref['source'],'provider':'Purdue campus ArcGIS','source_feature_id':b['fid'],'retrieved':'2026-10-22','raw_source_snapshot':'../official_purdue_buildings_wgs84.json','source_crs':'EPSG:4326','source_date':'not provided','transform':ref['coordinates'],'before':'Axis aligned generic rectangle auditorium and flytower conflicting with rotated rounded stepped official polygon. Before overlay saved.','after':'Exterior walls and roof registered to full official ground perimeter. Original geometry retained in hidden reference collection; incompatible site, facades, interior removed from export.','position_max_error_m':err,'orientation':'official polygon retained without simplification','height':'22.5m inherited main auditorium estimate; original flytower28.5m retained only in hidden reference because region lacks surveyed association','unresolved':'Roof levels, facade doors/windows, auditorium interior, exterior plaza need measured architectural reconstruction. Ground outline is authoritative map, not surveyed certification.','exported_objects':len(c.all_objects),'hidden_legacy_objects':len(old)},indent=2));print('CORRECTED',err)

